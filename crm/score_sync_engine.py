"""
LexiFlow CRM Score-Triggered Sync Engine

Uses lead qualification score as the primary trigger for CRM actions:
- Score >= 90: Auto-sync to Filevine as high-priority lead (create contact + project)
- Score >= 70: Auto-sync to Filevine as standard lead (create contact)
- Score >= 50: Flag for manual sync (pending human review)
- Score < 50: Store locally, no CRM action

Integrates with FilevineClient for enterprise push and uses the
integration map from market research for optimal field mapping.
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from crm.filevine import FilevineClient
from crm.clio import ClioGrowClient

logger = logging.getLogger(__name__)

# Score thresholds for automated CRM actions
SCORE_THRESHOLDS = {
    "auto_create_contact": 50,
    "auto_create_project": 70,
    "auto_create_high_priority": 90,
    "auto_medical_review": 75,
    "needs_human_review": 50,
}


@dataclass
class ScoreTriggeredAction:
    """Defines what CRM action to take based on lead score."""
    score: float
    action: str  # "create_contact", "create_project", "flag_review", "store_local"
    priority: str  # "high", "normal", "low"
    sync_filevine: bool = False
    sync_clio: bool = False
    sync_leaddock: bool = False
    notify_attorney: bool = False


def evaluate_score(score: float) -> ScoreTriggeredAction:
    """
    Evaluate a lead qualification score and determine the appropriate CRM action.
    
    Thresholds from the Filevine integration map:
    - 90+: High-priority Filevine project (contact + matter + custom fields)
    - 70-89: Standard Filevine contact with custom field scores
    - 50-69: Flag for human review in LeadDock
    - <50: Store locally only
    
    Args:
        score: AI-generated lead qualification score (0-100)
    
    Returns:
        ScoreTriggeredAction with routing instructions
    """
    if score >= 90:
        return ScoreTriggeredAction(
            score=score,
            action="create_project",
            priority="high",
            sync_filevine=True,
            sync_clio=True,
            sync_leaddock=True,
            notify_attorney=True
        )
    elif score >= 70:
        return ScoreTriggeredAction(
            score=score,
            action="create_contact",
            priority="normal",
            sync_filevine=True,
            sync_clio=True,
            sync_leaddock=True,
            notify_attorney=False
        )
    elif score >= 50:
        return ScoreTriggeredAction(
            score=score,
            action="flag_review",
            priority="low",
            sync_filevine=False,
            sync_clio=False,
            sync_leaddock=True,
            notify_attorney=False
        )
    else:
        return ScoreTriggeredAction(
            score=score,
            action="store_local",
            priority="none",
            sync_filevine=False,
            sync_clio=False,
            sync_leaddock=False,
            notify_attorney=False
        )


class ScoreTriggeredSyncEngine:
    """
    Orchestrates CRM sync actions based on lead qualification scores.
    
    Implements Phase 1 of the Filevine integration roadmap:
    1. Authenticate via OAuth 2.0
    2. Create contacts (leads) when score >= 70
    3. Create full projects when score >= 90
    4. Write custom fields per integration map recommendations
    5. Handle rate limiting and auth refresh
    
    Reference: /home/team/shared/research/filevine-api-integration-map.md
    """
    
    def __init__(self, filevine_client: Optional[FilevineClient] = None,
                 clio_client: Optional[ClioGrowClient] = None):
        self.filevine = filevine_client
        self.clio = clio_client
    
    async def process_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a lead through the score-triggered pipeline.
        
        Args:
            lead_data: Dict with keys including:
                - id: Lead ID
                - firstName, lastName: Contact names
                - email, phone: Contact info
                - qualificationScore: AI score (0-100)
                - medicalMerit: "High"|"Medium"|"Low"|"None"
                - caseType: Practice area
                - caseValue: Estimated case value
                - description: Case details
                - aiSummary: AI-generated summary
                - reviewUrl: Link to full LexiFlow analysis
                - sentimentScore: Lead urgency/sentiment (0-100)
                - filevineProjectTypeId: Filevine project type ID (firm-specific)
        
        Returns:
            Dict with sync results per CRM system
        """
        score = lead_data.get("qualificationScore", 0)
        action = evaluate_score(score)
        
        result = {
            "lead_id": lead_data.get("id"),
            "score": score,
            "action": action.action,
            "priority": action.priority,
            "sync_results": {}
        }
        
        # --- Filevine Sync (Phase 1: One-way push) ---
        if action.sync_filevine and self.filevine:
            try:
                fv_result = await self._sync_to_filevine(lead_data, action)
                result["sync_results"]["filevine"] = fv_result
                if fv_result.get("contactId"):
                    result["external_crm_id"] = fv_result["contactId"]
            except Exception as e:
                logger.error(f"Filevine sync failed: {e}")
                result["sync_results"]["filevine"] = {"status": "error", "detail": str(e)}
        
        # --- Clio Sync ---
        if action.sync_clio and self.clio:
            try:
                clio_result = await self._sync_to_clio(lead_data, action)
                result["sync_results"]["clio"] = clio_result
            except Exception as e:
                logger.error(f"Clio sync failed: {e}")
                result["sync_results"]["clio"] = {"status": "error", "detail": str(e)}
        
        # --- LeadDock Tracking ---
        if action.sync_leaddock:
            result["sync_results"]["leaddock"] = {"status": "recorded"}
        
        result["attorney_notified"] = action.notify_attorney
        return result
    
    async def _sync_to_filevine(self, lead: Dict[str, Any],
                                 action: ScoreTriggeredAction) -> Dict[str, Any]:
        if action.action == "create_project":
            project_data = {
                "projectName": (
                    f"{lead.get('firstName', '')} {lead.get('lastName', '')}"
                    f" - {lead.get('caseType', 'Intake')}"
                ),
                "typeId": lead.get("filevineProjectTypeId", ""),
                "customFields": {
                    "lexiflow_lead_score": str(lead.get("qualificationScore", 0)),
                    "lexiflow_medical_merit": lead.get("medicalMerit", "Not Assessed"),
                    "lexiflow_case_estimate": str(lead.get("caseValue", 0)),
                    "lexiflow_sentiment_score": str(lead.get("sentimentScore", 0)),
                    "lexiflow_review_link": lead.get("reviewUrl", ""),
                    "lexiflow_last_analyzed": lead.get("analyzedAt", ""),
                },
                "persons": [{
                    "firstName": lead.get("firstName", ""),
                    "lastName": lead.get("lastName", ""),
                    "email": lead.get("email", ""),
                    "phone": lead.get("phone", ""),
                    "type": "Client"
                }],
                "tags": ["LexiFlow", "AI-Qualified", "Priority-High"]
            }
            return await self.filevine.create_project(project_data)
        else:
            contact_data = {
                "firstName": lead.get("firstName", ""),
                "lastName": lead.get("lastName", ""),
                "email": lead.get("email", ""),
                "phone": lead.get("phone", ""),
                "contactType": "Lead",
                "status": "New",
                "tags": ["LexiFlow", "AI-Qualified"],
                "customFields": {
                    "lexiflow_lead_score": str(lead.get("qualificationScore", 0)),
                    "lexiflow_medical_merit": lead.get("medicalMerit", "Not Assessed"),
                    "lexiflow_review_link": lead.get("reviewUrl", ""),
                }
            }
            return await self.filevine.create_contact(contact_data)
    
    async def _sync_to_clio(self, lead: Dict[str, Any],
                            action: ScoreTriggeredAction) -> Dict[str, Any]:
        if self.clio is None:
            return {"status": "skipped", "reason": "Clio client not configured"}
        existing = await self.clio.search_contacts(
            email=lead.get("email"),
            phone=lead.get("phone")
        )
        if existing:
            return {
                "status": "skipped",
                "reason": "Contact already exists in Clio",
                "contact_id": existing[0].get("id")
            }
        contact_data = {
            "name": f"{lead.get('firstName', '')} {lead.get('lastName', '')}",
            "email": lead.get("email", ""),
            "phone_number": lead.get("phone", ""),
            "description": lead.get("description", ""),
            "custom_field_values": {
                "lead_score": str(lead.get("qualificationScore", 0)),
                "source": "LexiFlow Technologies Inc Intake"
            }
        }
        if action.priority == "high":
            contact_data["status"] = "Hot Lead"
        else:
            contact_data["status"] = "New Lead"
        return await self.clio.create_lead(contact_data)