from fastapi import APIRouter, Depends
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.user import UserReadWithSocietes, UserUpdate

router = APIRouter()

@router.get("/me", response_model=UserReadWithSocietes)
async def read_user_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Obtenir le profil de l'utilisateur connecté, avec ses sociétés.
    """
    result = await db.execute(
        select(User).options(selectinload(User.societes)).where(User.id == current_user.id)
    )
    user = result.scalars().first()
    return user

@router.patch("/me", response_model=UserReadWithSocietes)
async def update_user_me(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_in: UserUpdate,
) -> Any:
    """
    Mettre à jour le profil de l'utilisateur connecté.
    """
    if user_in.nom is not None:
        current_user.nom = user_in.nom
    if user_in.prenom is not None:
        current_user.prenom = user_in.prenom
    if user_in.email is not None:
        current_user.email = user_in.email

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    
    # Re-fetch with societies
    result = await db.execute(
        select(User).options(selectinload(User.societes)).where(User.id == current_user.id)
    )
    user = result.scalars().first()
    return user

@router.delete("/me")
async def delete_user_me(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Supprimer l'utilisateur actuellement connecté et toutes ses données associées.
    """
    await db.delete(current_user)
    await db.commit()
    return {"status": "success", "message": "Compte supprimé avec succès"}
