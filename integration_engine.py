import os
import json
import httpx
import logging
import asyncio
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# --- Retry Helper ---
async def retry_with_backoff(func, max_retries=3, base_delay=1.0):
    """Execute async function with exponential backoff retry."""
    last_exception = None
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Retry {attempt+1}/{max_retries} after {delay}s: {str(e)}")
                await asyncio.sleep(delay)
    raise last_exception

class IntegrationClient:
    """
    Client for production legal CRM APIs.
    Handles auth and specific payload structures for Clio Grow (Lexicata) and Filevine.
    """
    def __init__(self, firm_config: Dict[str, Any]):
        self.config = firm_config
        # Clio Grow (Lexicata) Production API
        self.clio_base_url = "https://grow.clio.com/api/v1"
        # Filevine Production API
        self.filevine_base_url = "https://api.filevine.io"
        self.leaddock_base_url = "https://api.leaddock.com"

    async def sync_to_clio(self, mapped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a lead in Clio Grow via Lexicata API"""
        auth_token = self.config.get("clio_auth_token") or self.config.get("lexicata_auth_token")
        if not auth_token:
            return {"status": "error", "message": "Clio/Lexicata Auth Token missing"}

        # Wrap in the expected Lexicata structure
        payload = {
            "auth_token": auth_token,
            "inbox_lead": mapped_data
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.clio_base_url}/inbox_leads",
                    json=payload
                )
                if response.status_code in [200, 201]:
                    data = response.json()
                    return {"status": "success", "external_id": data.get("id")}
                else:
                    logger.error(f"Clio Sync Error: {response.status_code} - {response.text}")
                    return {"status": "error", "message": f"Clio API error: {response.status_code}"}
            except Exception as e:
                logger.error(f"Clio Connection Exception: {str(e)}")
                return {"status": "error", "message": str(e)}

    async def sync_to_filevine(self, mapped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a lead/project in Filevine via direct API"""
        api_key = self.config.get("filevine_api_key")
        session_id = self.config.get("filevine_session_id")
        
        if not api_key:
            return {"status": "error", "message": "Filevine API credentials missing"}
        if not session_id:
            return {"status": "error", "message": "Filevine Session ID required for direct API"}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.filevine_base_url}/projects",
                    json=mapped_data,
                    headers={
                        "x-fv-apikey": api_key,
                        "x-fv-sessionid": session_id
                    }
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    return {"status": "success", "external_id": str(data.get("id") or data.get("projectId"))}
                else:
                    logger.error(f"Filevine Sync Error: {response.status_code} - {response.text}")
                    return {"status": "error", "message": f"Filevine API error: {response.status_code}"}
            except Exception as e:
                logger.error(f"Filevine Connection Exception: {str(e)}")
                return {"status": "error", "message": str(e)}

    async def sync_to_leaddock(self, mapped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a lead in LeadDock via API key auth"""
        api_key = self.config.get("leaddock_api_key")
        
        if not api_key:
            return {"status": "error", "message": "LeadDock API key missing"}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.leaddock_base_url}/leads",
                    json=mapped_data,
                    headers={"x-api-key": api_key}
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    return {"status": "success", "external_id": str(data.get("id"))}
                else:
                    logger.error(f"LeadDock Sync Error: {response.status_code} - {response.text}")
                    return {"status": "error", "message": f"LeadDock API error: {response.status_code}"}
            except Exception as e:
                logger.error(f"LeadDock Connection Exception: {str(e)}")
                return {"status": "error", "message": str(e)}

    async def search_leaddock_by_email(self, email: str) -> Optional[str]:
        """Check if a lead with given email already exists in LeadDock. Returns external_id if found."""
        api_key = self.config.get("leaddock_api_key")
        if not api_key or not email:
            return None
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.leaddock_base_url}/leads",
                    params={"email": email},
                    headers={"x-api-key": api_key}
                )
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        return str(data[0].get("id"))
                return None
            except:
                return None

    async def search_filevine_by_email(self, email: str) -> Optional[str]:
        """Check if a contact with given email exists in Filevine."""
        api_key = self.config.get("filevine_api_key")
        session_id = self.config.get("filevine_session_id")
        if not api_key or not session_id or not email:
            return None
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.filevine_base_url}/contacts",
                    params={"email": email},
                    headers={
                        "x-fv-apikey": api_key,
                        "x-fv-sessionid": session_id
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        return str(data[0].get("contactId"))
                return None
            except:
                return None

class UniversalLeadMapper:
    @staticmethod
    def map_lead(lead, target_system: str) -> Dict[str, Any]:
        name_parts = (lead.full_name or "Anonymous").split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else "Lead"
        
        summary = lead.ai_summary or "Synced from LexiFlow AI"
        
        if target_system == "clio":
            return {
                "from_first": first_name,
                "from_last": last_name,
                "from_email": lead.email,
                "from_phone": lead.phone,
                "from_message": summary,
                "referring_url": "LexiFlow AI"
            }
        elif target_system == "filevine":
            return {
                "firstName": first_name,
                "lastName": last_name,
                "email": lead.email,
                "phone": lead.phone,
                "summary": summary,
                "source": "LexiFlow AI",
                "projectName": f"{first_name} {last_name} - {lead.case_type or 'Intake'}",
                "referenceNumber": f"LEX-{lead.id}",
                "description": summary
            }
        elif target_system == "leaddock":
            return {
                "firstName": first_name,
                "lastName": last_name,
                "email": lead.email or "",
                "phone": lead.phone or "",
                "caseType": lead.case_type or "General Intake",
                "description": lead.description or summary,
                "source": "LexiFlow AI",
                "score": lead.qualification_score or 0,
                "caseValue": lead.case_value_estimate or 0,
                "notes": f"AI Summary: {summary}",
                "externalId": f"LEX-{lead.id}"
            }
        elif target_system == "mycase":
            return {
                "first_name": first_name,
                "last_name": last_name,
                "email": lead.email,
                "phone": lead.phone,
                "case_description": summary,
                "lead_source": "LexiFlow AI"
            }
        return {}

class IntegrationEngine:
    def __init__(self):
        self.mapper = UniversalLeadMapper()

    async def sync_lead(self, lead, system: str) -> Dict[str, Any]:
        """Sync a single lead to a single CRM system."""
        payload = self.mapper.map_lead(lead, system)
        firm = lead.firm
        
        production_mode = firm.production_sync_enabled if firm else False
        
        config = {}
        if firm and firm.api_config_json:
            try:
                config = json.loads(firm.api_config_json)
            except:
                pass
        
        if not production_mode:
            logger.info(f"SIMULATION: Syncing lead {lead.id} to {system}")
            return {
                "status": "success",
                "message": f"Successfully mapped and synced to {system.capitalize()} (Simulation)",
                "simulated": True,
                "payload_sent": payload
            }
        
        client = IntegrationClient(config)
        
        # Deduplication: search by email before creating
        if lead.email:
            try:
                if system == "leaddock":
                    existing = await retry_with_backoff(lambda: client.search_leaddock_by_email(lead.email), max_retries=2)
                    if existing:
                        logger.info(f"Lead {lead.id}: Already exists in LeadDock as {existing}, skipping")
                        return {"status": "skipped", "external_id": existing, "message": "Already exists in LeadDock"}
                elif system == "filevine":
                    existing = await retry_with_backoff(lambda: client.search_filevine_by_email(lead.email), max_retries=2)
                    if existing:
                        logger.info(f"Lead {lead.id}: Already exists in Filevine as {existing}, skipping")
                        return {"status": "skipped", "external_id": existing, "message": "Already exists in Filevine"}
            except Exception as e:
                logger.warning(f"Dedup check failed for {system}: {str(e)} — proceeding with create")
        
        # Perform sync with retry
        sync_funcs = {
            "clio": lambda: client.sync_to_clio(payload),
            "filevine": lambda: client.sync_to_filevine(payload),
            "leaddock": lambda: client.sync_to_leaddock(payload),
        }
        
        func = sync_funcs.get(system)
        if not func:
            return {"status": "error", "message": f"Production sync for {system} is not yet implemented."}
        
        try:
            return await retry_with_backoff(func, max_retries=3, base_delay=1.0)
        except Exception as e:
            logger.error(f"All retries exhausted for {system} sync: {str(e)}")
            return {"status": "error", "message": f"Sync failed after retries: {str(e)}"}

    async def sync_lead_auto(self, lead, db: Session = None) -> Dict[str, Any]:
        """
        Auto-sync a lead to all configured CRMs based on qualification score.
        Implements score-based routing:
        - >= 70: sync to Filevine + LeadDock
        - >= 50: sync to LeadDock only
        - < 50: hold for manual review
        """
        score = lead.qualification_score or 0
        firm = lead.firm
        
        # Determine targets based on score
        targets = []
        config = {}
        if firm and firm.api_config_json:
            try:
                config = json.loads(firm.api_config_json)
            except:
                pass
        
        sync_min_score = config.get("sync_min_score", 70)
        custom_targets = config.get("sync_targets", [])
        
        if score >= sync_min_score:
            # High-value: send to all configured CRMs
            if custom_targets:
                targets = custom_targets
            else:
                targets = ["filevine", "leaddock"]
        elif score >= 50:
            # Medium: send to LeadDock only
            targets = ["leaddock"]
        else:
            # Low: hold
            pass
        
        results = {}
        for system in targets:
            result = await self.sync_lead(lead, system)
            results[system] = result
            
            # Update lead's external IDs and status
            if result.get("status") == "success" and result.get("external_id"):
                if system == "filevine":
                    lead.external_crm_id = result["external_id"]
                lead.sync_status = f"Synced ({system.capitalize()})"
            elif result.get("external_id"):
                lead.sync_status = f"Already in {system.capitalize()}"
            
            # Log audit
            if db:
                from models import AuditLog
                log = AuditLog(
                    lead_id=lead.id,
                    action=f"sync_{system}_auto",
                    details=f"Score: {score}, Result: {result.get('status')}"
                )
                db.add(log)
        
        if targets:
            lead.last_sync_attempt = True  # Use a flag or timestamp
            if db:
                db.commit()
        
        return {
            "status": "complete" if targets else "held",
            "score": score,
            "targets": targets,
            "results": results
        }

    async def send_postmark_email(self, to_email: str, subject: str, body: str, firm=None) -> Dict[str, Any]:
        """Send an outbound email via Postmark API."""
        api_key = None
        if firm and firm.api_config_json:
            try:
                config = json.loads(firm.api_config_json)
                api_key = config.get("postmark_api_key")
            except:
                pass
        
        if not api_key:
            api_key = os.getenv("POSTMARK_SERVER_TOKEN")

        from_email = os.getenv("POSTMARK_FROM_EMAIL", "leads@lexiflow.co")
        
        if not api_key or "placeholder" in api_key.lower():
            logger.info(f"SIMULATED EMAIL to {to_email}: {subject}")
            return {"status": "success", "simulated": True}

        payload = {
            "From": from_email,
            "To": to_email,
            "Subject": subject,
            "TextBody": body,
            "MessageStream": "outbound"
        }

        async with httpx.AsyncClient() as client:
            try:
                res = await client.post(
                    "https://api.postmarkapp.com/email",
                    json=payload,
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                        "X-Postmark-Server-Token": api_key
                    }
                )
                return res.json()
            except Exception as e:
                logger.error(f"Postmark send failed: {str(e)}")
                return {"status": "error", "message": str(e)}

    async def push_to_github(self, firm, repo_full_name: str, branch: str, file_path: str, content: str, commit_message: str) -> Dict[str, Any]:
        """
        Push content to a GitHub repository.
        repo_full_name: e.g. "owner/repo"
        """
        config = {}
        if firm and firm.api_config_json:
            try:
                config = json.loads(firm.api_config_json)
            except:
                pass
        
        github_token = config.get("github_token") or os.getenv("GITHUB_TOKEN")
        
        if not github_token:
            return {"status": "error", "message": "GitHub token not configured for this firm."}
            
        async with httpx.AsyncClient() as client:
            try:
                headers = {
                    "Authorization": f"token {github_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                
                url = f"https://api.github.com/repos/{repo_full_name}/contents/{file_path}"
                params = {"ref": branch}
                
                res = await client.get(url, headers=headers, params=params)
                sha = None
                if res.status_code == 200:
                    sha = res.json().get("sha")
                
                import base64
                encoded_content = base64.b64encode(content.encode()).decode()
                
                payload = {
                    "message": commit_message,
                    "content": encoded_content,
                    "branch": branch
                }
                if sha:
                    payload["sha"] = sha
                    
                res = await client.put(url, headers=headers, json=payload)
                
                if res.status_code in [200, 201]:
                    return {"status": "success", "url": res.json().get("content", {}).get("html_url")}
                else:
                    logger.error(f"GitHub Push Error: {res.status_code} - {res.text}")
                    return {"status": "error", "message": f"GitHub API error: {res.status_code}", "details": res.text}
            except Exception as e:
                logger.error(f"GitHub Connection Exception: {str(e)}")
                return {"status": "error", "message": str(e)}

integration_engine = IntegrationEngine()
