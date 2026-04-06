from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.api import deps
from app.models.rapport import Rapport
from app.models.client import Client
from app.models.user import User
from app.schemas.rapport import Rapport as RapportSchema, RapportCreate, RapportUpdate

router = APIRouter()

@router.get("", response_model=List[RapportSchema])
async def read_rapports(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Récupère la liste des rapports de l'utilisateur connecté.
    """
    result = await db.execute(
        select(Rapport)
        .options(joinedload(Rapport.client))
        .where(Rapport.id_user == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

@router.post("", response_model=RapportSchema)
async def create_rapport(
    rapport_in: RapportCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Crée un nouveau rapport pour l'utilisateur connecté.
    """
    # Verify that the client belongs to the current user
    client_result = await db.execute(
        select(Client).where(Client.id == rapport_in.id_client, Client.id_user == current_user.id)
    )
    client_obj = client_result.scalars().first()
    if not client_obj:
        raise HTTPException(status_code=400, detail="Client invalide ou non autorisé")
        
    db_rapport = Rapport(**rapport_in.model_dump(), id_user=current_user.id)
    db.add(db_rapport)
    await db.commit()
    await db.refresh(db_rapport)
    db_rapport.client = client_obj
    return db_rapport

@router.get("/{rapport_id}", response_model=RapportSchema)
async def read_rapport(
    rapport_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Récupère un rapport spécifique.
    """
    result = await db.execute(
        select(Rapport)
        .options(joinedload(Rapport.client))
        .where(Rapport.id == rapport_id, Rapport.id_user == current_user.id)
    )
    rapport = result.scalars().first()
    if not rapport:
        raise HTTPException(status_code=404, detail="Rapport non trouvé")
    return rapport

@router.put("/{rapport_id}", response_model=RapportSchema)
async def update_rapport(
    rapport_id: int,
    rapport_in: RapportUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Met à jour un rapport existant.
    """
    result = await db.execute(
        select(Rapport)
        .options(joinedload(Rapport.client))
        .where(Rapport.id == rapport_id, Rapport.id_user == current_user.id)
    )
    db_rapport = result.scalars().first()
    
    if not db_rapport:
        raise HTTPException(status_code=404, detail="Rapport non trouvé")
        
    if rapport_in.id_client is not None and rapport_in.id_client != db_rapport.id_client:
        client_result = await db.execute(
            select(Client).where(Client.id == rapport_in.id_client, Client.id_user == current_user.id)
        )
        new_client = client_result.scalars().first()
        if not new_client:
            raise HTTPException(status_code=400, detail="Client invalide ou non autorisé")
        db_rapport.client = new_client

    update_data = rapport_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_rapport, field, value)
        
    await db.commit()
    await db.refresh(db_rapport)
    return db_rapport

@router.delete("/{rapport_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rapport(
    rapport_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Supprime un rapport.
    """
    result = await db.execute(
        select(Rapport).where(Rapport.id == rapport_id, Rapport.id_user == current_user.id)
    )
    db_rapport = result.scalars().first()
    
    if not db_rapport:
        raise HTTPException(status_code=404, detail="Rapport non trouvé")
        
    await db.delete(db_rapport)
    await db.commit()
    return None
