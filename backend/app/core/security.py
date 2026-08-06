import hashlib
import base64
import secrets
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _pre_hash(password: str) -> str:
    # Hash password with SHA-256 and base64 encode it before bcrypt
    # This avoids bcrypt's 72-character limit and handles any character length.
    return base64.b64encode(hashlib.sha256(password.encode("utf-8")).digest()).decode("ascii")

def verify_password(plain_password: str, hashed_password: Optional[str]) -> bool:
    if hashed_password is None:
        return False
    return pwd_context.verify(_pre_hash(plain_password), hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(_pre_hash(password))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_email_verification_token(email: str) -> str:
    """Generate a JWT token for email verification."""
    expire = datetime.utcnow() + timedelta(hours=settings.EMAIL_VERIFICATION_EXPIRE_HOURS)
    to_encode = {"sub": email, "purpose": "email_verify", "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_email_token(token: str) -> Optional[str]:
    """Verify an email verification token. Returns the email if valid, None otherwise."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("purpose") != "email_verify":
            return None
        return payload.get("sub")
    except JWTError:
        return None

def create_waiting_token(email: str) -> str:
    """Generate a JWT token used to listen to WebSocket while waiting for email verification."""
    expire = datetime.utcnow() + timedelta(hours=2)
    to_encode = {"sub": email, "purpose": "waiting_verify", "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_waiting_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("purpose") != "waiting_verify":
            return None
        return payload.get("sub")
    except JWTError:
        return None


def create_password_reset_token(email: str) -> str:
    """Generate a JWT token for password reset."""
    expire = datetime.utcnow() + timedelta(minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES)
    to_encode = {"sub": email, "purpose": "password_reset", "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify a password reset token. Returns the email if valid, None otherwise."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("purpose") != "password_reset":
            return None
        return payload.get("sub")
    except JWTError:
        return None
