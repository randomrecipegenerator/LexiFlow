"""
LexiFlow JWT Authentication Module.
Provides token creation, verification, and dependency injection for protected routes.
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext

from database import get_db
from models import User, Firm

logger = logging.getLogger(__name__)

# Secret key from environment or default for development
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "lexiflow-desktop-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash a plain text password."""
    return pwd_context.hash(password)


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
        # Look up desktop API key
        firm = db.query(Firm).filter(Firm.api_config_json.contains(x_api_key)).first()
        if firm:
            # Create a virtual user context for API key auth
            return type("DesktopUser", (), {
                "id": 0, "firm_id": firm.id, "email": f"desktop@{firm.slug}.local",
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