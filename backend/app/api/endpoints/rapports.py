from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.api import deps
from app.models.rapport import Rapport
from app.models.devis import Devis
from app.models.client import Client
from app.models.user import User
from app.schemas.rapport import Rapport as RapportSchema, RapportCreate, RapportUpdate

router = APIRouter()

@router.get("", response_model=List[RapportSchema])
async def read_rapports(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(deps.get_db),
    societe_id: int = Depends(deps.get_user_societe_id)
):
    """
    Récupère la liste des rapports de l'utilisateur connecté.
    """
    result = await db.execute(
        select(Rapport)
        .options(joinedload(Rapport.client), joinedload(Rapport.devis))
        .where(Rapport.id_societe == societe_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

@router.post("", response_model=RapportSchema)
async def create_rapport(
    rapport_in: RapportCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.require_permission("can_create_rapports")),
    societe_id: int = Depends(deps.get_user_societe_id),
    _: User = Depends(deps.check_trial_active)
):
    """
    Crée un nouveau rapport pour l'utilisateur connecté.
    """
    client_obj = None
    if rapport_in.id_client is not None:
        # Verify that the client belongs to the current user
        client_result = await db.execute(
            select(Client).where(Client.id == rapport_in.id_client, Client.id_societe == societe_id)
        )
        client_obj = client_result.scalars().first()
        if not client_obj:
            raise HTTPException(status_code=400, detail="Client invalide ou non autorisé")
            
    db_rapport = Rapport(**rapport_in.model_dump(), id_user=current_user.id, id_societe=societe_id)
    db.add(db_rapport)
    await db.commit()
    
    # Reload with joins to prevent MissingGreenlet error during serialization
    result = await db.execute(
        select(Rapport)
        .options(joinedload(Rapport.client), joinedload(Rapport.devis))
        .where(Rapport.id == db_rapport.id)
    )
    return result.scalars().first()

@router.get("/{rapport_id}", response_model=RapportSchema)
async def read_rapport(
    rapport_id: int,
    db: AsyncSession = Depends(deps.get_db),
    societe_id: int = Depends(deps.get_user_societe_id)
):
    """
    Récupère un rapport spécifique.
    """
    result = await db.execute(
        select(Rapport)
        .options(joinedload(Rapport.client), joinedload(Rapport.devis))
        .where(Rapport.id == rapport_id, Rapport.id_societe == societe_id)
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
    current_user: User = Depends(deps.require_permission("can_create_rapports")),
    societe_id: int = Depends(deps.get_user_societe_id),
    _: User = Depends(deps.check_trial_active)
):
    """
    Met à jour un rapport existant.
    """
    result = await db.execute(
        select(Rapport)
        .options(joinedload(Rapport.client))
        .where(Rapport.id == rapport_id, Rapport.id_societe == societe_id)
    )
    db_rapport = result.scalars().first()
    
    if not db_rapport:
        raise HTTPException(status_code=404, detail="Rapport non trouvé")
        
    if rapport_in.id_client is not None and rapport_in.id_client != db_rapport.id_client:
        client_result = await db.execute(
            select(Client).where(Client.id == rapport_in.id_client, Client.id_societe == societe_id)
        )
        new_client = client_result.scalars().first()
        if not new_client:
            raise HTTPException(status_code=400, detail="Client invalide ou non autorisé")
        db_rapport.client = new_client

    update_data = rapport_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_rapport, field, value)
    
    # Bidirectional link: if id_devis is updated, update the Devis to point to this rapport
    if "id_devis" in update_data and update_data["id_devis"] is not None:
        devis_result = await db.execute(
            select(Devis).where(Devis.id == update_data["id_devis"], Devis.id_societe == societe_id)
        )
        db_devis = devis_result.scalars().first()
        if db_devis:
            db_devis.id_rapport = db_rapport.id
    elif "id_devis" in update_data and update_data["id_devis"] is None:
        # If unlinking, also unlink from the other side
        devis_result = await db.execute(
            select(Devis).where(Devis.id_rapport == db_rapport.id)
        )
        db_devis = devis_result.scalars().first()
        if db_devis:
            db_devis.id_rapport = None
        
    await db.commit()
    
    # Reload with joins to prevent MissingGreenlet error during serialization
    reload_result = await db.execute(
        select(Rapport)
        .options(joinedload(Rapport.client), joinedload(Rapport.devis))
        .where(Rapport.id == db_rapport.id)
    )
    return reload_result.scalars().first()

@router.delete("/{rapport_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rapport(
    rapport_id: int,
    db: AsyncSession = Depends(deps.get_db),
    societe_id: int = Depends(deps.get_user_societe_id)
):
    """
    Supprime un rapport.
    """
    result = await db.execute(
        select(Rapport).where(Rapport.id == rapport_id, Rapport.id_societe == societe_id)
    )
    db_rapport = result.scalars().first()
    
    if not db_rapport:
        raise HTTPException(status_code=404, detail="Rapport non trouvé")
        
    await db.delete(db_rapport)
    await db.commit()
    return None
