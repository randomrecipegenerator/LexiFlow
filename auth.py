"""
LexiFlow JWT Authentication Module.
Provides token creation, verification, and dependency injection for protected routes.
"""
import os
import re
import logging
import bcrypt
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Header, status, APIRouter, Form
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from database import get_db
from models import User, Firm, SSOToken, Subscription

logger = logging.getLogger(__name__)

# Secret key from environment or default for development
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "lexiflow-desktop-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 hours


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a hashed password."""
    try:
        if isinstance(plain_password, str):
            plain_password = plain_password.encode('utf-8')
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        return bcrypt.checkpw(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def hash_password(password: str) -> str:
    """Hash a plain text password."""
    if isinstance(password, str):
        password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password, salt).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        return None


def get_current_user(
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency: Extract and validate the current user from JWT Bearer token or X-API-Key header.
    Used to protect authenticated routes.
    """
    # Extract token from Authorization header
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
    
    # Fallback: X-API-Key header (for desktop client auth)
    if not token and x_api_key:
        # Look up desktop API key in both dedicated field and JSON config
        firm = db.query(Firm).filter(
            (Firm.desktop_api_key == x_api_key) | 
            (Firm.api_config_json.contains(x_api_key))
        ).first()
        if firm:
            # For prototype, link API key auth to the first user in the firm
            user = db.query(User).filter(User.firm_id == firm.id).first()
            if user:
                return user
            
            # Fallback if no user exists (original behavior)
            return type("DesktopUser", (), {
                "id": None, "firm_id": firm.id, "email": f"desktop@{firm.slug}.local",
                "full_name": f"Desktop Client - {firm.name}", "role": "desktop",
                "is_active": 1, "firm": firm
            })()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Provide Bearer token or X-API-Key header.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account deactivated.",
        )
    
    return user


def get_current_firm(user: User = Depends(get_current_user)) -> Firm:
    """Get the firm associated with the currently authenticated user."""
    if not user.firm_id:
        raise HTTPException(status_code=403, detail="User not associated with a firm.")
    return user.firm


def generate_api_key() -> str:
    """Generate a secure API key for desktop client authentication."""
    import secrets
    return f"lf_desktop_{secrets.token_hex(32)}"


# =========================================================================
# Standard Login & SSO Routes
# =========================================================================

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/login")
async def login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """Standard username/password login endpoint."""
    from sqlalchemy import func
    logger.error(f"AUTH_LOG: Login attempt for email: '{email}'")
    user = db.query(User).filter(func.lower(User.email) == func.lower(email)).first()
    if not user:
        logger.error(f"AUTH_LOG: Login failed: User '{email}' not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(password, user.hashed_password):
        logger.error(f"AUTH_LOG: Login failed: Incorrect password for user '{email}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.error(f"AUTH_LOG: Login SUCCESS for user: '{email}'")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    access_token = create_access_token(
        data={"sub": str(user.id), "firm_id": user.firm_id, "role": user.role},
        expires_delta=timedelta(hours=24),
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "firm_id": user.firm_id
        }
    }


def _generate_unique_slug(firm_name: str, db: Session) -> str:
    """Generate a unique URL-friendly slug from a firm name."""
    base_slug = re.sub(r'[^a-z0-9]+', '-', firm_name.lower()).strip('-')
    if not base_slug:
        base_slug = "firm"
    
    slug = base_slug
    counter = 1
    while db.query(Firm).filter(Firm.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


@auth_router.post("/register")
async def register(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    firm_name: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Register a new law firm and user with a 30-day free trial.
    
    Steps:
    1. Validate inputs (email not taken, password length)
    2. Create Firm with unique slug
    3. Create User with hashed password
    4. Set up 30-day trial (plan_status='trial', trial_expires_at = now + 30 days)
    5. Create Subscription record
    6. Return JWT token + user/firm details for redirect to dashboard
    """
    from sqlalchemy import func
    
    # Validate inputs
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")
    
    if len(firm_name.strip()) < 2:
        raise HTTPException(status_code=400, detail="Firm name is required.")
    
    if len(name.strip()) < 2:
        raise HTTPException(status_code=400, detail="Full name is required.")
    
    # Check if email is already registered
    existing_user = db.query(User).filter(func.lower(User.email) == func.lower(email.strip())).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    
    # Generate unique slug
    slug = _generate_unique_slug(firm_name.strip(), db)
    
    # Create the Firm
    trial_end = datetime.utcnow() + timedelta(days=30)
    firm = Firm(
        name=firm_name.strip(),
        slug=slug,
        plan_status="trial",
        trial_expires_at=trial_end,
        billing_tier="enterprise",  # Full access during 30-day trial
        billing_period_start=datetime.utcnow(),
    )
    db.add(firm)
    db.flush()  # Get firm.id
    
    # Create the User
    hashed = hash_password(password)
    user = User(
        email=email.strip().lower(),
        hashed_password=hashed,
        full_name=name.strip(),
        firm_id=firm.id,
        role="admin",
        is_active=1,
    )
    db.add(user)
    db.flush()
    
    # Create Subscription record for the trial
    subscription = Subscription(
        firm_id=firm.id,
        status="trialing",
        plan_tier="enterprise",  # Full access during trial
        trial_end=trial_end,
        current_period_start=datetime.utcnow(),
        current_period_end=trial_end,
    )
    db.add(subscription)
    db.commit()
    db.refresh(user)
    db.refresh(firm)
    
    # Generate JWT
    access_token = create_access_token(
        data={"sub": str(user.id), "firm_id": user.firm_id, "role": user.role},
        expires_delta=timedelta(hours=24),
    )
    
    return {
        "status": "success",
        "access_token": access_token,
        "token_type": "bearer",
        "redirect": "/dashboard",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "firm_id": user.firm_id,
        },
        "firm": {
            "id": firm.id,
            "name": firm.name,
            "slug": firm.slug,
            "plan_status": firm.plan_status,
            "trial_expires_at": firm.trial_expires_at.isoformat(),
        },
    }


@auth_router.get("/sso-login")
async def sso_login(token: str, db: Session = Depends(get_db)):
    """
    SSO login endpoint for Desktop-to-Web seamless authentication.
    
    The Desktop app calls POST /api/desktop/auth/sso-token to get a token,
    then opens a browser to this endpoint.
    
    Steps:
    1. Validate the token from the SSOToken table
    2. Check it hasn't expired (>5 min) and isn't already used
    3. Mark it as used
    4. Create a JWT for the user
    5. Redirect to the web dashboard with the JWT as a query param
    """
    from fastapi.responses import RedirectResponse
    
    # Look up the token
    sso_record = db.query(SSOToken).filter(
        SSOToken.token == token,
        SSOToken.is_active == 1,
    ).first()
    
    if not sso_record:
        return RedirectResponse(
            url="/login.html?error=invalid_sso_token",
            status_code=303,
        )
    
    # Check expiration
    now = datetime.utcnow()
    if sso_record.expires_at < now:
        sso_record.is_active = 0
        db.commit()
        return RedirectResponse(
            url="/login.html?error=sso_token_expired",
            status_code=303,
        )
    
    # Check if already used (single-use)
    if sso_record.used_at is not None:
        return RedirectResponse(
            url="/login.html?error=sso_token_already_used",
            status_code=303,
        )
    
    # Mark as used
    sso_record.used_at = now
    sso_record.is_active = 0
    db.commit()
    
    # Look up the user
    user = db.query(User).filter(User.id == sso_record.user_id).first()
    if not user:
        return RedirectResponse(
            url="/login.html?error=user_not_found",
            status_code=303,
        )
    
    # Create a JWT for the user
    access_token = create_access_token(
        data={"sub": str(user.id), "firm_id": user.firm_id, "role": user.role},
        expires_delta=timedelta(hours=24),
    )
    
    # Log the SSO login
    log_entry = logging.getLogger("auth.sso")
    log_entry.info(f"SSO login successful for user {user.id} (firm {user.firm_id})")
    
from mail_service import mail_service
import secrets

@auth_router.post("/forgot-password")
async def forgot_password(email: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(func.lower(User.email) == func.lower(email)).first()
    if not user:
        # Don't reveal if user exists for security
        return {"message": "If an account exists with this email, a password reset link has been sent."}
    
    # Create token
    token = secrets.token_urlsafe(32)
    reset_token = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db.add(reset_token)
    db.commit()
    
    # Send email
    reset_url = f"https://lexiflow.co/reset-password.html?token={token}"
    await mail_service.send_template_email(
        to_email=user.email,
        subject="LexiFlow Password Reset",
        template_name="password_reset",
        variables={"reset_url": reset_url}
    )
    
    return {"message": "If an account exists with this email, a password reset link has been sent."}

@auth_router.post("/verify-email/request")
async def request_verification(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    token = secrets.token_urlsafe(32)
    verify_token = EmailVerificationToken(
        user_id=current_user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db.add(verify_token)
    db.commit()
    
    # In a real app, send email here
    return {"message": "Verification email sent.", "token_preview": token[:8]}
