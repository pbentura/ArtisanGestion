from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Any

from app.api.deps import get_db, get_current_user, is_admin
from app.models.societe import Societe
from app.models.user import User
from app.schemas.societe import SocieteCreate, SocieteRead

router = APIRouter()

@router.get("/me", response_model=SocieteRead)
async def get_my_societe(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Récupérer la société de l'utilisateur connecté.
    """
    result = await db.execute(
        select(Societe).where(Societe.id_user == current_user.id)
    )
    societe = result.scalar_one_or_none()
    
    if not societe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucune société trouvée pour cet utilisateur"
        )
    
    return societe

@router.put("/me", response_model=SocieteRead)
async def update_my_societe(
    societe_update: SocieteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Mettre à jour la société de l'utilisateur connecté.
    """
    result = await db.execute(
        select(Societe).where(Societe.id_user == current_user.id)
    )
    societe = result.scalar_one_or_none()
    
    if not societe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucune société trouvée pour cet utilisateur"
        )
    
    # Mettre à jour tous les champs
    for field, value in societe_update.model_dump().items():
        setattr(societe, field, value)
    
    await db.commit()
    await db.refresh(societe)
    return societe

@router.post("", response_model=SocieteRead, status_code=status.HTTP_201_CREATED)
async def create_societe(
    societe_in: SocieteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Créer une nouvelle société pour l'utilisateur connecté.
    """
    new_societe = Societe(
        id_user=current_user.id,
        **societe_in.model_dump()
    )
    db.add(new_societe)
    await db.commit()
    await db.refresh(new_societe)
    return new_societe
