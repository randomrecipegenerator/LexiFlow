"""
LexiFlow Desktop Backend API — Sync & Local-First Support.

Provides endpoints for the LexiFlow Desktop (Electron) application to:
1. Register & authenticate desktop clients
2. Sync local folder metadata with cloud
3. Coordinate PII/PHI redaction
4. Manage discovery vault sync jobs
5. SSO flow for Desktop-to-Web seamless login

All endpoints secured with JWT authentication (Bearer token) or X-API-Key.
"""
import logging
import os
import uuid
import json
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Header, Query, Body, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models import Firm, User, AuditLog, Lead as LeadModel, DesktopFolder, DesktopDocument, SSOToken
from auth import get_current_user, get_current_firm, generate_api_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/desktop", tags=["Desktop Client"])


# =========================================================================
# Pydantic Schemas
# =========================================================================

class FolderRegistration(BaseModel):
    """Request to register a local folder for sync."""
    local_path: str
    label: str = ""
    case_name: Optional[str] = None
    case_id: Optional[str] = None
    watch_subfolders: bool = True
    file_extensions: List[str] = [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".docx", ".txt"]


class FolderSyncStatus(BaseModel):
    """Status update for a synced folder."""
    folder_id: str
    status: str  # "scanning", "syncing", "idle", "error"
    total_files: int = 0
    synced_files: int = 0
    pending_files: int = 0
    error_message: Optional[str] = None


class RedactionRequest(BaseModel):
    """Request to perform PII/PHI redaction on a document."""
    document_id: str
    file_path: str
    file_name: str
    redaction_types: List[str] = ["ssn", "dob", "patient_id", "medical_record_number", "name", "address"]
    local_only: bool = True  # True = redact locally, False = send to cloud


class DocumentMetadata(BaseModel):
    """Metadata for a synced document."""
    file_name: str
    file_path: str
    file_size_bytes: int
    file_hash: str
    mime_type: str
    folder_id: str
    case_id: Optional[str] = None
    tags: List[str] = []


# =========================================================================
# Auth Endpoints
# =========================================================================

@router.post("/auth/register-client")
async def register_desktop_client(
    device_name: str = Body(...),
    device_id: str = Body(...),
    os_info: str = Body(""),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Register a desktop client device for a firm.
    Returns an API key that the desktop app stores locally.
    """
    api_key = generate_api_key()
    client_id = str(uuid.uuid4())
    
    # In production, save to a DesktopClient table.
    # For now, we update the Firm's api_config_json to include this key.
    firm = db.query(Firm).filter(Firm.id == user.firm_id).first()
    if firm:
        config = {}
        if firm.api_config_json:
            try:
                config = json.loads(firm.api_config_json)
            except:
                pass
        
        # Add or update desktop keys
        if "desktop_keys" not in config:
            config["desktop_keys"] = []
        
        config["desktop_keys"].append({
            "client_id": client_id,
            "api_key": api_key,
            "device_name": device_name,
            "registered_at": datetime.utcnow().isoformat()
        })
        
        # Also set it as the primary desktop key for easier lookup in auth.py
        config["desktop_api_key"] = api_key
        
        firm.api_config_json = json.dumps(config)
        db.add(firm)
    
    # Log the registration
    log = AuditLog(
        firm_id=user.firm_id, user_id=user.id,
        action="desktop_client_registered",
        category="desktop",
        details=f"Device: {device_name} ({device_id})",
    )
    db.add(log)
    db.commit()
    
    return {
        "status": "registered",
        "client_id": client_id,
        "api_key": api_key,
        "note": "Store this API key securely in the desktop app's local config.",
    }


@router.get("/auth/clients")
async def list_desktop_clients(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all registered desktop clients for the firm."""
    firm = db.query(Firm).filter(Firm.id == user.firm_id).first()
    if not firm or not firm.api_config_json:
        return {"clients": [], "total": 0}
        
    try:
        config = json.loads(firm.api_config_json)
        clients = config.get("desktop_keys", [])
        # Hide actual API keys
        safe_clients = [{k: v for k, v in c.items() if k != "api_key"} for c in clients]
        return {"clients": safe_clients, "total": len(safe_clients)}
    except:
        return {"clients": [], "total": 0}


# =========================================================================
# SSO Flow — Desktop-to-Web Seamless Login
# =========================================================================

@router.post("/auth/sso-token")
async def create_sso_token(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a short-lived SSO token for Desktop-to-Web login.
    
    The Desktop app calls this with its API key to get a token,
    then opens a browser to /api/auth/sso-login?token=XYZ
    which validates the token, sets a session, and redirects to the dashboard.
    
    Token expires in 5 minutes and is single-use.
    """
    import secrets
    from datetime import timedelta
    
    # Generate a secure random token
    token = secrets.token_urlsafe(48)
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    
    # Persist to database
    sso = SSOToken(
        firm_id=user.firm_id,
        user_id=user.id,
        token=token,
        expires_at=expires_at,
    )
    db.add(sso)
    db.commit()
    
    # Log the SSO token creation
    log = AuditLog(
        firm_id=user.firm_id, user_id=user.id,
        action="sso_token_created",
        category="auth",
        details=f"SSO token created, expires at {expires_at.isoformat()}",
    )
    db.add(log)
    db.commit()
    
    return {
        "token": token,
        "expires_at": expires_at.isoformat(),
        "login_url": f"/api/auth/sso-login?token={token}",
        "note": "This token is single-use and expires in 5 minutes. "
                "Open the login_url in a browser to complete SSO login.",
    }


# =========================================================================
# Folder Sync Endpoints
# =========================================================================

@router.post("/folders/register")
async def register_folder(
    folder: FolderRegistration,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Register a local folder for Discovery-Vault sync.
    The desktop app calls this when a user selects a folder to watch.
    """
    folder_uuid = str(uuid.uuid4())
    
    db_folder = DesktopFolder(
        firm_id=user.firm_id,
        folder_uuid=folder_uuid,
        local_path=folder.local_path,
        label=folder.label or folder.local_path.split("/")[-1] or folder.local_path.split("\\")[-1],
        case_name=folder.case_name,
        case_id=folder.case_id,
        watch_subfolders=1 if folder.watch_subfolders else 0,
        file_extensions=json.dumps(folder.file_extensions),
        status="registered"
    )
    db.add(db_folder)
    
    # Audit log
    log = AuditLog(
        firm_id=user.firm_id, user_id=user.id,
        action="folder_registered",
        category="desktop",
        details=f"Folder: {folder.local_path} (Case: {folder.case_name or 'N/A'})",
    )
    db.add(log)
    db.commit()
    
    return {
        "status": "registered",
        "folder_id": folder_uuid,
        "label": db_folder.label,
    }


@router.get("/folders")
async def list_folders(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all registered sync folders for the firm."""
    folders = db.query(DesktopFolder).filter(DesktopFolder.firm_id == user.firm_id).all()
    
    result = []
    for f in folders:
        result.append({
            "folder_id": f.folder_uuid,
            "local_path": f.local_path,
            "label": f.label,
            "case_name": f.case_name,
            "status": f.status,
            "total_files": f.total_files,
            "synced_files": f.synced_files,
            "registered_at": f.registered_at.isoformat() if f.registered_at else None,
            "last_synced_at": f.last_synced_at.isoformat() if f.last_synced_at else None,
        })
        
    return {"folders": result, "total": len(result)}


@router.get("/folders/{folder_id}")
async def get_folder_status(
    folder_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get sync status for a specific folder."""
    folder = db.query(DesktopFolder).filter(
        DesktopFolder.folder_uuid == folder_id,
        DesktopFolder.firm_id == user.firm_id
    ).first()
    
    if not folder:
        raise HTTPException(404, detail="Folder not found")
        
    return {
        "folder_id": folder.folder_uuid,
        "status": folder.status,
        "total_files": folder.total_files,
        "synced_files": folder.synced_files,
        "last_synced_at": folder.last_synced_at.isoformat() if folder.last_synced_at else None,
    }


@router.put("/folders/{folder_id}/sync-status")
async def update_folder_sync_status(
    folder_id: str,
    status_update: FolderSyncStatus,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update sync status for a folder (called by desktop client)."""
    folder = db.query(DesktopFolder).filter(
        DesktopFolder.folder_uuid == folder_id,
        DesktopFolder.firm_id == user.firm_id
    ).first()
    
    if not folder:
        raise HTTPException(404, detail="Folder not found")
    
    folder.status = status_update.status
    folder.total_files = status_update.total_files
    folder.synced_files = status_update.synced_files
    
    if status_update.status == "idle":
        folder.last_synced_at = datetime.utcnow()
    
    db.commit()
    return {"status": "updated", "folder_id": folder_id}


# =========================================================================
# Document Sync Endpoints
# =========================================================================

@router.post("/documents/sync")
async def sync_document_metadata(
    documents: List[DocumentMetadata],
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Sync document metadata from the desktop client to the cloud.
    The desktop app sends metadata for files it finds during folder scanning.
    """
    for doc in documents:
        # Check if document already exists
        existing = db.query(DesktopDocument).filter(
            DesktopDocument.file_hash == doc.file_hash,
            DesktopDocument.firm_id == user.firm_id
        ).first()
        
        if not existing:
            new_doc = DesktopDocument(
                firm_id=user.firm_id,
                folder_uuid=doc.folder_id,
                file_name=doc.file_name,
                file_path=doc.file_path,
                file_size_bytes=doc.file_size_bytes,
                file_hash=doc.file_hash,
                mime_type=doc.mime_type,
                case_id=doc.case_id,
                tags=json.dumps(doc.tags)
            )
            db.add(new_doc)
    
    db.commit()
    
    # Audit log for batch sync
    log = AuditLog(
        firm_id=user.firm_id, user_id=user.id,
        action="documents_synced",
        category="desktop",
        details=f"Synced {len(documents)} documents from desktop client",
    )
    db.add(log)
    db.commit()
    
    return {
        "status": "synced",
        "count": len(documents)
    }


@router.get("/documents/search")
async def search_documents(
    query: str = Query(""),
    folder_id: Optional[str] = Query(None),
    case_id: Optional[str] = Query(None),
    file_type: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
):
    """
    Search synced document metadata.
    In production, this would query a Document table in the database.
    For the prototype, returns a placeholder response.
    """
    # TODO: In production, query a documents table
    return {
        "query": query,
        "folder_id": folder_id,
        "case_id": case_id,
        "results": [],
        "total": 0,
        "note": "Document search available in production with full DB integration.",
    }


# =========================================================================
# PII/PHI Redaction Endpoints
# =========================================================================

@router.post("/redact")
async def request_redaction(
    request: RedactionRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Request PII/PHI redaction for a document.
    If local_only=True, the desktop app performs redaction locally.
    If local_only=False, the file is uploaded to cloud for redaction.
    """
    redaction_id = str(uuid.uuid4())
    
    # Log the redaction request
    log = AuditLog(
        firm_id=user.firm_id, user_id=user.id,
        action="redaction_requested",
        category="desktop",
        details=f"Document: {request.file_name}, Types: {', '.join(request.redaction_types)}, Local: {request.local_only}",
    )
    db.add(log)
    db.commit()
    
    return {
        "status": "redaction_requested",
        "redaction_id": redaction_id,
        "strategy": "local" if request.local_only else "cloud",
        "document_id": request.document_id,
        "redaction_types": request.redaction_types,
        "instructions": (
            "Desktop: Apply redaction locally using the specified redaction types. "
            "Return the redacted file path and a redaction log."
        ) if request.local_only else (
            "Upload the document to the cloud redaction endpoint for processing."
        ),
    }


@router.post("/redact/confirm")
async def confirm_redaction(
    redaction_id: str = Body(...),
    document_id: str = Body(...),
    redacted_file_path: str = Body(...),
    redacted_fields_count: int = Body(0),
    redaction_log: dict = Body({}),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Confirm that local redaction was completed.
    Called by the desktop app after it finishes redacting a document locally.
    """
    log = AuditLog(
        firm_id=user.firm_id, user_id=user.id,
        action="redaction_completed",
        category="desktop",
        details=f"Redaction {redaction_id}: {redacted_fields_count} fields redacted in {document_id}",
    )
    db.add(log)
    db.commit()
    
    return {
        "status": "confirmed",
        "redaction_id": redaction_id,
        "document_id": document_id,
        "redacted_fields_count": redacted_fields_count,
    }


# =========================================================================
# Desktop Health & Config
# =========================================================================

@router.get("/health")
async def desktop_health():
    """Health check for desktop API connectivity."""
    return {
        "status": "healthy",
        "service": "LexiFlow Desktop Backend",
        "version": "1.0.0",
        "api_version": "v1",
    }


@router.get("/config/{firm_id}")
async def get_desktop_config(
    firm_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get desktop client configuration for a firm."""
    if user.firm_id != firm_id:
        raise HTTPException(403, detail="Access denied")
    
    firm = db.query(Firm).filter(Firm.id == firm_id).first()
    if not firm:
        raise HTTPException(404, detail="Firm not found")
    
    return {
        "firm_id": firm.id,
        "firm_name": firm.name,
        "firm_slug": firm.slug,
        "sync_endpoint": "/api/desktop/folders/register",
        "redaction_endpoint": "/api/desktop/redact",
        "supported_file_types": [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".docx", ".txt", ".csv"],
        "max_file_size_mb": 50,
        "sync_interval_seconds": 300,  # 5 minutes default
        "redact_locally_by_default": True,
    }


# =========================================================================
# Desktop CRM Integration — Clio & Filevine Workflows
# =========================================================================

@router.get("/crm/config")
async def get_desktop_crm_config(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get CRM configuration for the firm.
    Returns which systems are configured and their status.
    Used by the Desktop app to show connection status in settings.
    """
    firm = db.query(Firm).filter(Firm.id == user.firm_id).first()
    if not firm:
        raise HTTPException(404, detail="Firm not found")

    config = {}
    if firm.api_config_json:
        try:
            config = json.loads(firm.api_config_json)
        except json.JSONDecodeError:
            pass

    return {
        "firm_id": firm.id,
        "production_sync_enabled": bool(firm.production_sync_enabled),
        "filevine": {
            "configured": bool(config.get("filevine_api_key")),
            "org_id": (config.get("filevine_org_id", "")[:12] + "...") if config.get("filevine_org_id") else None,
        },
        "clio": {
            "configured": bool(config.get("clio_client_id")),
            "has_token": bool(config.get("clio_access_token")),
        },
        "sync_min_score": config.get("sync_min_score", 70),
    }


@router.put("/crm/config")
async def update_desktop_crm_config(
    config_data: dict = Body(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update CRM configuration from the Desktop app.
    Accepts Filevine (api_key, api_secret, org_id) and Clio (client_id, client_secret) credentials.
    """
    firm = db.query(Firm).filter(Firm.id == user.firm_id).first()
    if not firm:
        raise HTTPException(404, detail="Firm not found")

    current = {}
    if firm.api_config_json:
        try:
            current = json.loads(firm.api_config_json)
        except json.JSONDecodeError:
            pass

    # Merge new config
    allowed_keys = [
        "filevine_api_key", "filevine_api_secret", "filevine_session_id", "filevine_org_id",
        "clio_client_id", "clio_client_secret", "clio_access_token", "clio_refresh_token", "clio_redirect_uri",
        "sync_min_score", "sync_targets",
    ]
    for key, value in config_data.items():
        if key in allowed_keys and value is not None:
            current[key] = value

    firm.api_config_json = json.dumps(current)
    db.commit()

    # Audit log
    log = AuditLog(
        firm_id=user.firm_id, user_id=user.id,
        action="crm_config_updated",
        category="crm",
        details=f"Updated CRM config: {', '.join(config_data.keys())}",
    )
    db.add(log)
    db.commit()

    return {"status": "updated", "configured_systems": list(config_data.keys())}


@router.post("/crm/test/{system}")
async def test_desktop_crm_connection(
    system: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Test connection to a configured CRM system from the Desktop app.
    system: "filevine", "clio", or "leaddock"
    """
    firm = db.query(Firm).filter(Firm.id == user.firm_id).first()
    if not firm:
        raise HTTPException(404, detail="Firm not found")

    config = {}
    if firm.api_config_json:
        try:
            config = json.loads(firm.api_config_json)
        except json.JSONDecodeError:
            pass

    if system == "filevine":
        api_key = config.get("filevine_api_key", "")
        return {
            "system": "filevine",
            "configured": bool(api_key),
            "status": "ok" if api_key else "not_configured",
            "message": "Filevine API key is configured" if api_key else "Filevine not configured. Add your API key in settings.",
        }
    elif system == "clio":
        client_id = config.get("clio_client_id", "")
        has_token = bool(config.get("clio_access_token"))
        return {
            "system": "clio",
            "configured": bool(client_id),
            "status": "ok" if has_token else "needs_auth",
            "auth_url": f"https://app.clio.com/oauth/authorize?client_id={client_id}&redirect_uri={config.get('clio_redirect_uri', 'http://localhost:3000/callback')}&response_type=code"
                if client_id and not has_token else None,
        }
    elif system == "leaddock":
        api_key = config.get("leaddock_api_key", "")
        return {
            "system": "leaddock",
            "configured": bool(api_key),
            "status": "ok" if api_key else "not_configured",
        }

    return {"system": system, "status": "unknown_system"}


@router.post("/crm/sync/{lead_id}")
async def trigger_desktop_crm_sync(
    lead_id: int,
    system: str = Query("auto", description="CRM system (auto, filevine, clio)"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Trigger a CRM sync for a specific lead from the Desktop app.
    Delegates to the existing integration_engine for the actual sync.
    """
    from integration_engine import integration_engine as engine

    lead = db.query(LeadModel).filter(
        LeadModel.id == lead_id,
        LeadModel.firm_id == user.firm_id
    ).first()
    if not lead:
        raise HTTPException(404, detail="Lead not found")

    if system == "auto":
        result = await engine.sync_lead_auto(lead, db)
    else:
        result = await engine.sync_lead(lead, system)

    # Audit log
    log = AuditLog(
        firm_id=user.firm_id, user_id=user.id,
        action=f"desktop_crm_sync_{system}",
        category="crm",
        details=f"Lead {lead_id}: {result.get('status')}",
    )
    db.add(log)
    db.commit()

    return {
        "lead_id": lead_id,
        "system": system,
        "result": result,
    }


@router.post("/crm/sync-all-pending")
async def trigger_desktop_bulk_sync(
    min_score: float = Query(70.0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Sync all qualified leads to configured CRMs from the Desktop app.
    """
    from integration_engine import integration_engine as engine

    leads = db.query(LeadModel).filter(
        LeadModel.firm_id == user.firm_id,
        LeadModel.qualification_score >= min_score,
        LeadModel.status.in_(["New", "Qualified"])
    ).all()

    results = []
    for lead in leads:
        result = await engine.sync_lead_auto(lead, db)
        results.append({
            "lead_id": lead.id,
            "name": lead.full_name,
            "score": lead.qualification_score,
            "status": result.get("status"),
        })

    return {"total": len(results), "synced": results}


@router.get("/crm/sync-history")
async def get_desktop_sync_history(
    limit: int = Query(50, le=200),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get CRM sync history for the Desktop app."""
    logs = db.query(AuditLog).filter(
        AuditLog.firm_id == user.firm_id,
        AuditLog.action.like("crm_%"),
    ).order_by(AuditLog.id.desc()).limit(limit).all()

    return {
        "total": len(logs),
        "logs": [
            {
                "id": log.id,
                "action": log.action,
                "details": log.details,
                "timestamp": str(log.created_at) if log.created_at else None,
            }
            for log in logs
        ],
    }


@router.get("/crm/stats")
async def get_desktop_crm_stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get CRM statistics for the Desktop app dashboard."""
    total_leads = db.query(LeadModel).filter(LeadModel.firm_id == user.firm_id).count()
    synced = db.query(LeadModel).filter(
        LeadModel.firm_id == user.firm_id,
        LeadModel.sync_status.notlike("%Not%")
    ).count()
    pending = db.query(LeadModel).filter(
        LeadModel.firm_id == user.firm_id,
        LeadModel.esign_status == "Pending"
    ).count()

    return {
        "total_leads": total_leads,
        "synced_to_crm": synced,
        "pending_esign": pending,
        "sync_rate": round(synced / total_leads * 100, 1) if total_leads > 0 else 0,
    }