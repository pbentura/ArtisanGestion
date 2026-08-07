from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.schemas.token import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/auth/login")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les identifiants",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenPayload(sub=username)
    except JWTError:
        raise credentials_exception
        
    result = await db.execute(select(User).where(User.email == token_data.sub))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user


def is_admin(user: User) -> bool:
    """Retourne True si l'utilisateur a le rôle ADMIN."""
    return getattr(user, "role", None) == "ADMIN"

def get_trial_days_remaining(user: User) -> int:
    if is_admin(user):
        return 9999
    if not hasattr(user, "date_inscription") or not user.date_inscription:
        return 0
    now = datetime.now(timezone.utc)
    # user.date_inscription should be an aware datetime, but if naive, make it aware
    date_inscr = user.date_inscription
    if date_inscr.tzinfo is None:
        date_inscr = date_inscr.replace(tzinfo=timezone.utc)
        
    delta = now - date_inscr
    remaining = 14 - delta.days
    return max(0, remaining)

def check_trial_active(current_user: User = Depends(get_current_user)) -> User:
    """Dependency qui lève une exception si l'essai est terminé."""
    if get_trial_days_remaining(current_user) == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Votre période d'essai est terminée. Veuillez souscrire à un abonnement."
        )
    return current_user
