from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

from app.api import deps
from app.models.client import Client
from app.models.user import User
from app.schemas.client import Client as ClientSchema, ClientCreate, ClientUpdate

router = APIRouter()

@router.get("", response_model=List[ClientSchema])
async def read_clients(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(deps.get_db),
    societe_id: int = Depends(deps.get_user_societe_id)
):
    """
    Récupère la liste des clients de l'entreprise.
    """
    result = await db.execute(
        select(Client).where(Client.id_societe == societe_id).offset(skip).limit(limit)
    )
    return result.scalars().all()

@router.post("", response_model=ClientSchema)
async def create_client(
    client_in: ClientCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.require_permission("can_create_clients")),
    societe_id: int = Depends(deps.get_user_societe_id),
    _: User = Depends(deps.check_trial_active)
):
    """
    Crée un nouveau client pour l'entreprise.
    """
    db_client = Client(**client_in.model_dump(), id_user=current_user.id, id_societe=societe_id)
    db.add(db_client)
    await db.commit()
    await db.refresh(db_client)
    return db_client

@router.get("/{client_id}", response_model=ClientSchema)
async def read_client(
    client_id: int,
    db: AsyncSession = Depends(deps.get_db),
    societe_id: int = Depends(deps.get_user_societe_id)
):
    """
    Récupère un client spécifique.
    """
    result = await db.execute(
        select(Client).where(Client.id == client_id, Client.id_societe == societe_id)
    )
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    return client

@router.put("/{client_id}", response_model=ClientSchema)
async def update_client(
    client_id: int,
    client_in: ClientUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.require_permission("can_create_clients")),
    societe_id: int = Depends(deps.get_user_societe_id),
    _: User = Depends(deps.check_trial_active)
):
    """
    Met à jour un client existant.
    """
    result = await db.execute(
        select(Client).where(Client.id == client_id, Client.id_societe == societe_id)
    )
    db_client = result.scalars().first()
    
    if not db_client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
        
    update_data = client_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_client, field, value)
        
    await db.commit()
    await db.refresh(db_client)
    return db_client

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.require_permission("can_create_clients")),
    societe_id: int = Depends(deps.get_user_societe_id)
):
    """
    Supprime un client.
    """
    result = await db.execute(
        select(Client).where(Client.id == client_id, Client.id_societe == societe_id)
    )
    db_client = result.scalars().first()
    
    if not db_client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
        
    await db.delete(db_client)
    await db.commit()
    return None
