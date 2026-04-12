from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.api import deps
from app.models.devis import Devis
from app.models.client import Client
from app.models.user import User
from app.schemas.devis import Devis as DevisSchema, DevisCreate, DevisUpdate
from app.models.ligne_devis import LigneDevis

router = APIRouter()

@router.get("", response_model=List[DevisSchema])
async def read_devis(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Récupère la liste des devis de l'utilisateur connecté.
    """
    result = await db.execute(
        select(Devis)
        .options(joinedload(Devis.client), joinedload(Devis.lignes))
        .where(Devis.id_user == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    return result.unique().scalars().all()

@router.post("", response_model=DevisSchema)
async def create_devis(
    devis_in: DevisCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Crée un nouveau devis pour l'utilisateur connecté.
    """
    client_result = await db.execute(
        select(Client).where(Client.id == devis_in.id_client, Client.id_user == current_user.id)
    )
    client_obj = client_result.scalars().first()
    if not client_obj:
        raise HTTPException(status_code=400, detail="Client invalide ou non autorisé")
        
    devis_data = devis_in.model_dump(exclude={"lignes"})
    db_devis = Devis(**devis_data, id_user=current_user.id)
    
    if devis_in.lignes:
        for ligne_in in devis_in.lignes:
            ligne_data = ligne_in.model_dump()
            db_ligne = LigneDevis(**ligne_data)
            db_devis.lignes.append(db_ligne)

    db.add(db_devis)
    await db.commit()
    await db.refresh(db_devis)
    db_devis.client = client_obj
    return db_devis

from app.schemas.ligne_devis import LigneDevis as LigneDevisSchema

@router.get("/lignes/descriptions", response_model=List[LigneDevisSchema])
async def get_lignes_descriptions(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Récupère la liste des lignes complètes uniques (groupées par description) 
    pour proposer l'autocomplétion avancée.
    """
    result = await db.execute(
        select(LigneDevis)
        .join(Devis, LigneDevis.id_devis == Devis.id)
        .where(Devis.id_user == current_user.id)
        .order_by(LigneDevis.id.desc())
    )
    lignes = result.scalars().all()
    
    seen = set()
    unique_lignes = []
    for ligne in lignes:
        desc_lower = ligne.description.strip().lower()
        if desc_lower not in seen:
            seen.add(desc_lower)
            unique_lignes.append(ligne)
            
    return unique_lignes

async def read_un_devis(
    devis_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Récupère un devis spécifique.
    """
    result = await db.execute(
        select(Devis)
        .options(joinedload(Devis.client), joinedload(Devis.lignes))
        .where(Devis.id == devis_id, Devis.id_user == current_user.id)
    )
    devis = result.unique().scalars().first()
    if not devis:
        raise HTTPException(status_code=404, detail="Devis non trouvé")
    return devis

@router.put("/{devis_id}", response_model=DevisSchema)
async def update_devis(
    devis_id: int,
    devis_in: DevisUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Met à jour un devis existant (infos générales uniquement).
    """
    result = await db.execute(
        select(Devis)
        .options(joinedload(Devis.client), joinedload(Devis.lignes))
        .where(Devis.id == devis_id, Devis.id_user == current_user.id)
    )
    db_devis = result.unique().scalars().first()
    
    if not db_devis:
        raise HTTPException(status_code=404, detail="Devis non trouvé")
        
    if devis_in.id_client is not None and devis_in.id_client != db_devis.id_client:
        client_result = await db.execute(
            select(Client).where(Client.id == devis_in.id_client, Client.id_user == current_user.id)
        )
        new_client = client_result.scalars().first()
        if not new_client:
            raise HTTPException(status_code=400, detail="Client invalide ou non autorisé")
        db_devis.client = new_client

    update_data = devis_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_devis, field, value)
        
    await db.commit()
    await db.refresh(db_devis)
    return db_devis

@router.delete("/{devis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_devis(
    devis_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Supprime un devis.
    """
    result = await db.execute(
        select(Devis).where(Devis.id == devis_id, Devis.id_user == current_user.id)
    )
    db_devis = result.scalars().first()
    
    if not db_devis:
        raise HTTPException(status_code=404, detail="Devis non trouvé")
        
    await db.delete(db_devis)
    await db.commit()
    return None
