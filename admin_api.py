"""
LexiFlow Administrative API — Firm Onboarding & Platform Management.

Provides endpoints for LexiFlow Administrators to:
1. Authenticate administrative users
2. Manage firms and firm-level configurations
3. Oversee user accounts and roles
4. Monitor global audit logs and platform health
"""
import logging
import json
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Body, status, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models import Firm, User, AuditLog
from auth import (
    get_current_user, 
    verify_password, 
    create_access_token,
    get_current_firm
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Platform Administration"])

# =========================================================================
# Pydantic Schemas
# =========================================================================

class LoginRequest(BaseModel):
    email: str
    password: str

class UserInvite(BaseModel):
    email: str
    role: str = "attorney"

class RoleUpdate(BaseModel):
    role: str

class FirmUpdate(BaseModel):
    name: Optional[str] = None
    branding_colors: Optional[str] = None

class FirmRegister(BaseModel):
    firm_name: str
    admin_email: str
    password: str
    branding_colors: Optional[str] = None

# =========================================================================
# Authentication Endpoints
# =========================================================================

@router.post("/auth/login")
async def admin_login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate an administrative user.
    Returns a JWT access token if successful.
    """
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    if user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to administrators",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "firm_id": user.firm_id, "role": user.role}
    )
    
    # Log login
    log = AuditLog(
        user_id=user.id,
        firm_id=user.firm_id,
        action="admin_login_success",
        category="auth",
        details=f"Admin login successful for {user.email}"
    )
    db.add(log)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }

# =========================================================================
# Management Endpoints
# =========================================================================

@router.get("/dashboard")
async def get_admin_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get high-level platform statistics for the admin dashboard."""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
        
    total_firms = db.query(Firm).count()
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == 1).count()
    
    # Get recent firms
    recent_firms = db.query(Firm).order_by(Firm.id.desc()).limit(5).all()
    
    return {
        "stats": {
            "total_firms": total_firms,
            "total_users": total_users,
            "active_users": active_users,
            "platform_status": "healthy"
        },
        "recent_firms": [
            {"id": f.id, "name": f.name, "slug": f.slug, "plan": f.plan_status}
            for f in recent_firms
        ]
    }

@router.get("/audit-log")
async def get_global_audit_log(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve global audit logs for platform oversight."""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
        
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    
    result = []
    for log in logs:
        result.append({
            "id": log.id,
            "timestamp": log.timestamp.isoformat(),
            "action": log.action,
            "category": log.category,
            "details": log.details,
            "user_id": log.user_id,
            "firm_id": log.firm_id
        })
    return result

@router.get("/users")
async def list_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all users across the platform."""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
        
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
            "firm_id": u.firm_id,
            "created_at": u.created_at.isoformat() if u.created_at else None
        } for u in users
    ]

@router.post("/users/invite")
async def invite_user(
    invite: UserInvite,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Simulate inviting a new user to the platform."""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
        
    # In a real app, this would send an email and create a pending invitation
    # For the prototype, we log it and return success
    log = AuditLog(
        user_id=current_user.id,
        firm_id=current_user.firm_id,
        action="user_invited",
        category="users",
        details=f"Invited {invite.email} as {invite.role}"
    )
    db.add(log)
    db.commit()
    
    return {"status": "success", "message": f"Invitation sent to {invite.email}"}

@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    role_data: RoleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a user's platform role."""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    old_role = user.role
    user.role = role_data.role
    
    log = AuditLog(
        user_id=current_user.id,
        firm_id=current_user.firm_id,
        action="user_role_updated",
        category="users",
        details=f"User {user.email} role changed from {old_role} to {role_data.role}"
    )
    db.add(log)
    db.commit()
    
    return {"status": "success", "user_id": user_id, "new_role": user.role}

@router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate a user account."""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.is_active = 0
    
    log = AuditLog(
        user_id=current_user.id,
        firm_id=current_user.firm_id,
        action="user_deactivated",
        category="users",
        details=f"User {user.email} account deactivated"
    )
    db.add(log)
    db.commit()
    
    return {"status": "success", "message": "User account deactivated"}

@router.get("/firms/me")
async def get_current_firm_admin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get firm details for the currently authenticated admin."""
    firm = db.query(Firm).filter(Firm.id == current_user.firm_id).first()
    if not firm:
        raise HTTPException(status_code=404, detail="Firm not found")
    return {
        "id": firm.id,
        "name": firm.name,
        "slug": firm.slug,
        "billing_tier": firm.plan_status,
        "document_count": firm.document_count,
        "branding_colors": firm.branding_colors
    }

@router.post("/firms/register")
async def register_firm(
    reg_data: FirmRegister,
    db: Session = Depends(get_db)
):
    """Register a new firm and admin user."""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == reg_data.admin_email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Create firm
    from utils import slugify
    new_firm = Firm(
        name=reg_data.firm_name,
        slug=slugify(reg_data.firm_name),
        branding_colors=reg_data.branding_colors,
        plan_status="trial",
        billing_tier="enterprise",
        trial_expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db.add(new_firm)
    db.flush()
    
    # Create admin user
    from auth import hash_password
    new_user = User(
        email=reg_data.admin_email,
        hashed_password=hash_password(reg_data.password),
        role='admin',
        firm_id=new_firm.id,
        is_active=1
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(new_user.id), "firm_id": new_user.firm_id, "role": new_user.role}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "role": new_user.role
        },
        "firm": {
            "id": new_firm.id,
            "name": new_firm.name,
            "slug": new_firm.slug
        }
    }

@router.put("/firms/me")
async def update_current_firm_admin(
    firm_data: FirmUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the branding and name for the administrator's firm."""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
        
    firm = db.query(Firm).filter(Firm.id == current_user.firm_id).first()
    if not firm:
        raise HTTPException(status_code=404, detail="Firm not found")
        
    if firm_data.name:
        firm.name = firm_data.name
    if firm_data.branding_colors:
        firm.branding_colors = firm_data.branding_colors
        
    db.commit()
    return {"status": "success", "firm_name": firm.name}
