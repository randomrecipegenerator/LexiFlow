"""
FastAPI router for CRM integration endpoints.

Provides CRUD operations for firm CRM configurations,
manual and automatic sync triggers, and webhook registration.

All routes require authentication (firm slug header).
"""
import json
import logging
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Header, Body, Query
from sqlalchemy.orm import Session
import httpx

from database import get_db
from models import Firm, Lead, AuditLog
from crm.filevine import FilevineClient, FilevineConfig
from crm.clio import ClioGrowClient, ClioConfig
from integration_engine import integration_engine as engine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/crm", tags=["CRM Integration"])


# =========================================================================
# Firm CRM Configuration
# =========================================================================


def _get_firm(x_firm_slug: str = Header(None), db: Session = Depends(get_db)):
    """Dependency: get firm by slug from header."""
    if not x_firm_slug:
        raise HTTPException(status_code=400, detail="x-firm-slug header required")
    firm = db.query(Firm).filter(Firm.slug == x_firm_slug).first()
    if not firm:
        raise HTTPException(status_code=404, detail="Firm not found")
    return firm


@router.get("/config")
async def get_crm_config(firm: Firm = Depends(_get_firm)):
    """
    Get CRM configuration for a firm.
    Returns masked credentials (partial reveal only).
    """
    config = {}
    if firm.api_config_json:
        try:
            config = json.loads(firm.api_config_json)
        except json.JSONDecodeError:
            pass

    # Return only non-sensitive metadata + masked keys
    safe_config = {
        "production_sync_enabled": bool(firm.production_sync_enabled),
        "configured_systems": [],
        "sync_min_score": config.get("sync_min_score", 70),
        "sync_targets": config.get("sync_targets", []),
    }

    if config.get("filevine_api_key"):
        safe_config["configured_systems"].append("filevine")
        safe_config["filevine"] = {"org_id": config.get("filevine_org_id", "")[:8]}
    if config.get("clio_client_id"):
        safe_config["configured_systems"].append("clio")
        safe_config["clio"] = {"has_refresh_token": bool(config.get("clio_refresh_token"))}
    if config.get("leaddock_api_key"):
        safe_config["configured_systems"].append("leaddock")
        safe_config["leaddock"] = {"configured": True}

    return safe_config


@router.put("/config")
async def update_crm_config(
    config_data: Dict[str, Any] = Body(...),
    firm: Firm = Depends(_get_firm),
    db: Session = Depends(get_db)
):
    """
    Update CRM configuration for a firm.
    Accepts partial updates; only provided fields are changed.
    """
    current = {}
    if firm.api_config_json:
        try:
            current = json.loads(firm.api_config_json)
        except json.JSONDecodeError:
            pass

    # Merge new config into current
    for key, value in config_data.items():
        if value is not None:
            current[key] = value

    firm.api_config_json = json.dumps(current)
    db.commit()

    return {"status": "updated", "systems": list(config_data.keys())}


@router.post("/config/test")
async def test_crm_connection(
    system: str = Query(..., description="CRM system to test"),
    firm: Firm = Depends(_get_firm),
):
    """
    Test connection to a configured CRM system.
    Returns connection status without creating any data.
    """
    config = {}
    if firm.api_config_json:
        try:
            config = json.loads(firm.api_config_json)
        except json.JSONDecodeError:
            pass

    if system == "filevine":
        fv_config = FilevineConfig(
            api_key=config.get("filevine_api_key", ""),
            api_secret=config.get("filevine_api_secret", ""),
            session_id=config.get("filevine_session_id", ""),
            org_id=config.get("filevine_org_id", ""),
        )
        client = FilevineClient(fv_config)
        try:
            await client._ensure_auth()
            has_session = bool(client.config.session_id)
            return {"status": "ok" if has_session else "auth_failed", "system": "filevine"}
        finally:
            await client.close()

    elif system == "clio":
        clio_config = ClioConfig(
            client_id=config.get("clio_client_id", ""),
            client_secret=config.get("clio_client_secret", ""),
            access_token=config.get("clio_access_token", ""),
            refresh_token=config.get("clio_refresh_token", ""),
            redirect_uri=config.get("clio_redirect_uri", ""),
        )
        client = ClioGrowClient(clio_config)
        try:
            has_token = bool(clio_config.access_token)
            return {"status": "ok" if has_token else "needs_auth", "system": "clio"}
        finally:
            await client.close()

    elif system == "leaddock":
        api_key = config.get("leaddock_api_key", "")
        if not api_key or "placeholder" in api_key.lower():
            return {"status": "not_configured", "system": "leaddock"}
        async with httpx.AsyncClient() as http:
            try:
                resp = await http.get(
                    "https://api.leaddock.com/me",
                    headers={"x-api-key": api_key}
                )
                return {"status": "ok" if resp.status_code == 200 else "failed", "system": "leaddock"}
            except Exception as e:
                return {"status": "error", "detail": str(e), "system": "leaddock"}

    return {"status": "unknown_system", "system": system}


# =========================================================================
# Manual Sync Triggers
# =========================================================================


@router.post("/sync/{lead_id}")
async def sync_lead_to_crm(
    lead_id: int,
    system: str = Query("auto", description="CRM system (auto, filevine, clio, leaddock)"),
    firm: Firm = Depends(_get_firm),
    db: Session = Depends(get_db)
):
    """
    Manually sync a lead to one or all configured CRMs.

    - system="auto": Uses score-based routing (>=70 -> Filevine+LeadDock, >=50 -> LeadDock)
    - system="filevine"|"clio"|"leaddock": Sync to specific system
    """
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.firm_id == firm.id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if system == "auto":
        result = await engine.sync_lead_auto(lead, db)
    else:
        result = await engine.sync_lead(lead, system)

    # Log the sync attempt
    log = AuditLog(
        lead_id=lead.id,
        action=f"manual_sync_{system}",
        details=json.dumps({"system": system, "result": result.get("status")})
    )
    db.add(log)
    db.commit()

    return result


@router.post("/sync-all")
async def sync_all_qualified_leads(
    min_score: float = Query(70.0, description="Minimum qualification score"),
    firm: Firm = Depends(_get_firm),
    db: Session = Depends(get_db)
):
    """
    Sync all qualified leads (score >= min_score) to configured CRMs.
    """
    leads = db.query(Lead).filter(
        Lead.firm_id == firm.id,
        Lead.qualification_score >= min_score,
        Lead.status.in_(["New", "Qualified"])
    ).all()

    results = []
    for lead in leads:
        result = await engine.sync_lead_auto(lead, db)
        results.append({
            "lead_id": lead.id,
            "name": lead.full_name,
            "score": lead.qualification_score,
            "status": result.get("status")
        })

    return {"total": len(results), "results": results}


# =========================================================================
# Sync Status & History
# =========================================================================


@router.get("/sync-status/{lead_id}")
async def get_sync_status(
    lead_id: int,
    firm: Firm = Depends(_get_firm),
    db: Session = Depends(get_db)
):
    """Get sync status for a specific lead."""
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.firm_id == firm.id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    return {
        "lead_id": lead.id,
        "status": lead.sync_status or "Not Synced",
        "external_crm_id": lead.external_crm_id,
        "qualification_score": lead.qualification_score,
        "esigned": lead.esign_status == "Signed",
    }


@router.get("/history")
async def get_sync_history(
    limit: int = Query(50, le=200),
    firm: Firm = Depends(_get_firm),
    db: Session = Depends(get_db)
):
    """Get recent CRM sync audit logs for this firm."""
    logs = db.query(AuditLog).filter(
        AuditLog.firm_id == firm.id,
        AuditLog.action.like("sync_%")
    ).order_by(AuditLog.id.desc()).limit(limit).all()

    return [
        {
            "id": log.id,
            "lead_id": log.lead_id,
            "action": log.action,
            "details": log.details,
            "timestamp": str(log.created_at)
        }
        for log in logs
    ]


# =========================================================================
# Statistics
# =========================================================================


@router.get("/stats")
async def get_crm_stats(
    firm: Firm = Depends(_get_firm),
    db: Session = Depends(get_db)
):
    """Get CRM sync statistics for this firm."""
    total_leads = db.query(Lead).filter(Lead.firm_id == firm.id).count()
    synced = db.query(Lead).filter(
        Lead.firm_id == firm.id,
        Lead.sync_status.notlike("%Not%")
    ).count()
    pending_esign = db.query(Lead).filter(
        Lead.firm_id == firm.id,
        Lead.esign_status == "Pending"
    ).count()

    return {
        "total_leads": total_leads,
        "synced_to_crm": synced,
        "pending_esign": pending_esign,
        "production_mode": bool(firm.production_sync_enabled),
    }