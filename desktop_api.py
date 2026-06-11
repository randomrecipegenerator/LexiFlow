"""
LexiFlow Desktop Backend API — Sync & Local-First Support.

Provides endpoints for the LexiFlow Desktop (Electron) application to:
1. Register & authenticate desktop clients
2. Sync local folder metadata with cloud
3. Coordinate PII/PHI redaction
4. Manage discovery vault sync jobs

All endpoints secured with JWT authentication (Bearer token) or X-API-Key.
"""
import logging
import os
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Header, Query, Body, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models import Firm, User, AuditLog
from auth import get_current_user, get_current_firm, generate_api_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/desktop", tags=["Desktop Client"])


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
# In-Memory Store (for demo/prototype — move to DB in production)
# =========================================================================

# Simulated folder registrations (keyed by folder_id)
_registered_folders: dict = {}
_desktop_clients: dict = {}


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
    
    _desktop_clients[client_id] = {
        "client_id": client_id,
        "firm_id": user.firm_id,
        "device_name": device_name,
        "device_id": device_id,
        "os_info": os_info,
        "api_key": api_key,
        "registered_at": datetime.utcnow().isoformat(),
        "last_seen": datetime.utcnow().isoformat(),
        "is_active": True,
    }
    
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
):
    """List all registered desktop clients for the firm."""
    firm_clients = [
        {k: v for k, v in info.items() if k != "api_key"}  # Never expose API keys
        for cid, info in _desktop_clients.items()
        if info["firm_id"] == user.firm_id
    ]
    return {"clients": firm_clients, "total": len(firm_clients)}


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
    folder_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    _registered_folders[folder_id] = {
        "folder_id": folder_id,
        "firm_id": user.firm_id,
        "local_path": folder.local_path,
        "label": folder.label or folder.local_path.split("/")[-1] or folder.local_path.split("\\")[-1],
        "case_name": folder.case_name,
        "case_id": folder.case_id,
        "watch_subfolders": folder.watch_subfolders,
        "file_extensions": folder.file_extensions,
        "status": "registered",
        "total_files": 0,
        "synced_files": 0,
        "registered_at": now,
        "last_synced_at": None,
    }
    
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
        "folder_id": folder_id,
        "label": _registered_folders[folder_id]["label"],
    }


@router.get("/folders")
async def list_folders(
    user: User = Depends(get_current_user),
):
    """List all registered sync folders for the firm."""
    folders = [
        info for info in _registered_folders.values()
        if info["firm_id"] == user.firm_id
    ]
    return {"folders": folders, "total": len(folders)}


@router.get("/folders/{folder_id}")
async def get_folder_status(
    folder_id: str,
    user: User = Depends(get_current_user),
):
    """Get sync status for a specific folder."""
    folder = _registered_folders.get(folder_id)
    if not folder:
        raise HTTPException(404, detail="Folder not found")
    if folder["firm_id"] != user.firm_id:
        raise HTTPException(403, detail="Access denied")
    return folder


@router.put("/folders/{folder_id}/sync-status")
async def update_folder_sync_status(
    folder_id: str,
    status_update: FolderSyncStatus,
    user: User = Depends(get_current_user),
):
    """Update sync status for a folder (called by desktop client)."""
    folder = _registered_folders.get(folder_id)
    if not folder:
        raise HTTPException(404, detail="Folder not found")
    if folder["firm_id"] != user.firm_id:
        raise HTTPException(403, detail="Access denied")
    
    folder["status"] = status_update.status
    folder["total_files"] = status_update.total_files
    folder["synced_files"] = status_update.synced_files
    folder["pending_files"] = status_update.pending_files
    if status_update.error_message:
        folder["error_message"] = status_update.error_message
    if status_update.status == "idle":
        folder["last_synced_at"] = datetime.utcnow().isoformat()
    
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
    synced_count = len(documents)
    
    # Audit log for batch sync
    log = AuditLog(
        firm_id=user.firm_id, user_id=user.id,
        action="documents_synced",
        category="desktop",
        details=f"Synced {synced_count} documents from desktop client",
    )
    db.add(log)
    db.commit()
    
    return {
        "status": "synced",
        "count": synced_count,
        "documents": [
            {
                "file_name": d.file_name,
                "folder_id": d.folder_id,
                "sync_status": "metadata_recorded",
            }
            for d in documents
        ],
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