import hashlib
import base64
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _pre_hash(password: str) -> str:
    # Hash password with SHA-256 and base64 encode it before bcrypt
    # This avoids bcrypt's 72-character limit and handles any character length.
    return base64.b64encode(hashlib.sha256(password.encode("utf-8")).digest()).decode("ascii")

def verify_password(plain_password: str, hashed_password: str) -> bool:
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
