import os
import json
import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

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

class UniversalLeadMapper:
    @staticmethod
    def map_lead(lead, target_system: str) -> Dict[str, Any]:
        name_parts = (lead.full_name or "Anonymous").split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else "Lead"
        
        summary = lead.ai_summary or "Synced from LexiFlow AI"
        
        if target_system == "clio":
            # Mapping for Clio Grow (Lexicata API)
            return {
                "from_first": first_name,
                "from_last": last_name,
                "from_email": lead.email,
                "from_phone": lead.phone,
                "from_message": summary,
                "referring_url": "LexiFlow AI"
            }
        elif target_system == "filevine":
            # Hybrid mapping: LeadDock uses flat fields, Filevine Projects uses nested
            # We provide a structure that can be easily converted or used by either
            return {
                "firstName": first_name,
                "lastName": last_name,
                "email": lead.email,
                "phone": lead.phone,
                "summary": summary,
                "source": "LexiFlow AI",
                # Filevine Project specific fields (placeholders/derived)
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
        payload = self.mapper.map_lead(lead, system)
        firm = lead.firm
        
        # 1. Determine if we are in Production or Simulation mode
        production_mode = firm.production_sync_enabled if firm else False
        
        # 2. Get firm config
        config = {}
        if firm and firm.api_config_json:
            try:
                config = json.loads(firm.api_config_json)
            except:
                pass
        
        # 3. Execute Sync
        if not production_mode:
            logger.info(f"SIMULATION: Syncing lead {lead.id} to {system}")
            return {
                "status": "success",
                "message": f"Successfully mapped and synced to {system.capitalize()} (Simulation)",
                "simulated": True,
                "payload_sent": payload
            }
        
        # Production Sync Logic
        client = IntegrationClient(config)
        
        if system == "clio":
            return await client.sync_to_clio(payload)
        elif system == "filevine":
            return await client.sync_to_filevine(payload)
        elif system == "leaddock":
            return await client.sync_to_leaddock(payload)
        else:
            return {
                "status": "error",
                "message": f"Production sync for {system} is not yet implemented. Please use Simulation mode."
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
                # 1. Get the current file (to get SHA if it exists)
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
                
                # 2. Push content
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

