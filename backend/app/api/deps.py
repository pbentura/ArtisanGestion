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
from app.schemas.user import a_acces_equipe, jours_essai_restants
from app.models.societe import Societe
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

        # Les jetons à usage unique (vérification d'email, réinitialisation de mot de
        # passe, attente de vérification) sont signés avec la même clé : sans ce
        # contrôle ils feraient office de jeton d'accès complet.
        # Les jetons d'accès historiques n'ont pas de champ "purpose" : on les accepte.
        purpose = payload.get("purpose")
        if purpose not in (None, "access"):
            raise credentials_exception

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
    return jours_essai_restants(
        getattr(user, "role", None), getattr(user, "date_inscription", None)
    )


async def _utilisateur_de_reference(user: User, db: AsyncSession) -> User:
    """
    Compte qui porte réellement les droits.

    Un collaborateur a son propre compte, sans abonnement : c'est celui de son
    patron qui ouvre les droits. Sans cette résolution, un collaborateur d'une
    équipe abonnée serait bloqué 14 jours après *sa* propre inscription.
    """
    # On détermine l'entreprise active
    active_id = getattr(user, 'active_societe_id', None) or user.id_societe
    if not active_id:
        result = await db.execute(select(Societe.id).where(Societe.id_user == user.id))
        active_id = result.scalar()

    if active_id:
        result = await db.execute(select(Societe.id_user).where(Societe.id == active_id))
        owner_id = result.scalar()
        if owner_id and owner_id != user.id:
            # Si l'utilisateur consulte une entreprise qu'il ne possède pas, on
            # se réfère au propriétaire.
            owner_result = await db.execute(select(User).where(User.id == owner_id))
            owner = owner_result.scalars().first()
            if owner:
                return owner

    return user


async def resoudre_jours_essai(user: User, db: AsyncSession) -> int:
    """Jours d'essai restants, en tenant compte du propriétaire de l'entreprise."""
    return get_trial_days_remaining(await _utilisateur_de_reference(user, db))


async def resoudre_acces_equipe(user: User, db: AsyncSession) -> bool:
    """
    Droit aux fonctions du plan Équipe, propriétaire compris.

    L'essai de 14 jours donne accès au plan Équipe : voir
    ``app.schemas.user.a_acces_equipe`` pour la règle elle-même.
    """
    reference = await _utilisateur_de_reference(user, db)
    return a_acces_equipe(
        getattr(reference, "role", None), getattr(reference, "date_inscription", None)
    )


async def check_trial_active(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency qui lève une exception si l'essai est terminé."""
    if await resoudre_jours_essai(current_user, db) == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Votre période d'essai est terminée. Veuillez souscrire à un abonnement."
        )
    return current_user


def require_permission(permission: str):
    """Dependency factory qui vérifie qu'un utilisateur a une permission donnée."""
    async def check(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        if is_admin(current_user):
            return current_user
            
        # Si on est le propriétaire de la société active, on a tous les droits
        active_id = getattr(current_user, 'active_societe_id', None) or current_user.id_societe
        if not active_id:
            result = await db.execute(select(Societe.id).where(Societe.id_user == current_user.id))
            active_id = result.scalar()
            
        if active_id:
            result = await db.execute(select(Societe.id_user).where(Societe.id == active_id))
            owner_id = result.scalar()
            if owner_id == current_user.id:
                return current_user

        # Vérifier la permission spécifique
        if not getattr(current_user, permission, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous n'avez pas la permission pour cette action."
            )
        return current_user
    return check


async def get_user_societe_id(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> int:
    """Retourne l'id_societe active de l'utilisateur."""
    if getattr(current_user, 'active_societe_id', None):
        return current_user.active_societe_id
    if current_user.id_societe:
        return current_user.id_societe
    result = await db.execute(select(Societe).where(Societe.id_user == current_user.id))
    societe = result.scalars().first()
    if societe:
        return societe.id
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Aucune entreprise associée à cet utilisateur."
    )
