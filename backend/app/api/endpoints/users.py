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
        select(User)
        .options(selectinload(User.societes), selectinload(User.societe_membre))
        .where(User.id == current_user.id)
    )
    user = result.scalars().first()
    
    user_data = UserReadWithSocietes.model_validate(user)
    if not user.is_owner and user.societe_membre:
        from app.schemas.societe import SocieteRead
        user_data.societes = [SocieteRead.model_validate(user.societe_membre)]
        
    return user_data

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
    if hasattr(user_in, 'onboarding_draft') and user_in.onboarding_draft is not None:
        current_user.onboarding_draft = user_in.onboarding_draft
    elif "onboarding_draft" in user_in.model_dump(exclude_unset=True) and user_in.onboarding_draft is None:
        current_user.onboarding_draft = None

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    
    # Re-fetch with societies
    result = await db.execute(
        select(User)
        .options(selectinload(User.societes), selectinload(User.societe_membre))
        .where(User.id == current_user.id)
    )
    user = result.scalars().first()
    
    from app.core.websockets import manager
    await manager.broadcast_to_user(current_user.id, {
        "type": "SYNC_DRAFT",
        "data": user.onboarding_draft
    })
    
    user_data = UserReadWithSocietes.model_validate(user)
    if not user.is_owner and user.societe_membre:
        from app.schemas.societe import SocieteRead
        user_data.societes = [SocieteRead.model_validate(user.societe_membre)]
        
    return user_data

@router.delete("/me")
async def delete_user_me(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Supprimer l'utilisateur actuellement connecté et toutes ses données associées.
    """
    from sqlalchemy import delete, update, select
    from app.models.societe import Societe
    from app.models.invitation import Invitation
    from app.models.client import Client
    from app.models.devis import Devis
    from app.models.facture import Facture
    from app.models.rapport import Rapport
    from app.models.ligne_facture import LigneFacture
    from app.models.ligne_devis import LigneDevis

    uid = current_user.id
    is_owner = current_user.is_owner

    if is_owner:
        # L'utilisateur est propriétaire : on supprime son entreprise et toutes ses données
        result = await db.execute(select(Societe.id).where(Societe.id_user == uid))
        societes_ids = result.scalars().all()
        
        if societes_ids:
            # Détacher tous les membres de ces sociétés
            await db.execute(
                update(User).where(User.id_societe.in_(societes_ids)).values(id_societe=None, is_owner=False)
            )
            # Supprimer les invitations pour ces sociétés
            await db.execute(
                delete(Invitation).where(Invitation.id_societe.in_(societes_ids))
            )
            
            # Supprimer les documents de la société (même créés par des collaborateurs)
            factures_result = await db.execute(select(Facture.id).where(Facture.id_societe.in_(societes_ids)))
            factures_ids = factures_result.scalars().all()
            if factures_ids:
                await db.execute(delete(LigneFacture).where(LigneFacture.id_facture.in_(factures_ids)))
                
            devis_result = await db.execute(select(Devis.id).where(Devis.id_societe.in_(societes_ids)))
            devis_ids = devis_result.scalars().all()
            if devis_ids:
                await db.execute(delete(LigneDevis).where(LigneDevis.id_devis.in_(devis_ids)))

            await db.execute(delete(Facture).where(Facture.id_societe.in_(societes_ids)))
            await db.execute(delete(Devis).where(Devis.id_societe.in_(societes_ids)))
            await db.execute(delete(Rapport).where(Rapport.id_societe.in_(societes_ids)))
            await db.execute(delete(Client).where(Client.id_societe.in_(societes_ids)))
            await db.execute(delete(Societe).where(Societe.id.in_(societes_ids)))
            
    else:
        # L'utilisateur est juste collaborateur
        # On transfère la propriété de ses documents au propriétaire de l'entreprise
        if current_user.id_societe:
            soc_result = await db.execute(select(Societe).where(Societe.id == current_user.id_societe))
            societe = soc_result.scalars().first()
            if societe:
                owner_id = societe.id_user
                await db.execute(update(Facture).where(Facture.id_user == uid).values(id_user=owner_id))
                await db.execute(update(Devis).where(Devis.id_user == uid).values(id_user=owner_id))
                await db.execute(update(Rapport).where(Rapport.id_user == uid).values(id_user=owner_id))
                await db.execute(update(Client).where(Client.id_user == uid).values(id_user=owner_id))

    # Détacher l'utilisateur courant
    await db.execute(update(User).where(User.id == uid).values(id_societe=None))
    
    # 2. Supprimer les invitations envoyées par l'utilisateur
    await db.execute(delete(Invitation).where(Invitation.invited_by == uid))
    
    # 3. Documents orphelins (si créés hors d'une société)
    factures_result = await db.execute(select(Facture.id).where(Facture.id_user == uid))
    factures_ids = factures_result.scalars().all()
    if factures_ids:
        await db.execute(delete(LigneFacture).where(LigneFacture.id_facture.in_(factures_ids)))
        
    devis_result = await db.execute(select(Devis.id).where(Devis.id_user == uid))
    devis_ids = devis_result.scalars().all()
    if devis_ids:
        await db.execute(delete(LigneDevis).where(LigneDevis.id_devis.in_(devis_ids)))

    await db.execute(delete(Facture).where(Facture.id_user == uid))
    await db.execute(delete(Devis).where(Devis.id_user == uid))
    await db.execute(delete(Rapport).where(Rapport.id_user == uid))
    await db.execute(delete(Client).where(Client.id_user == uid))
    
    # 5. Supprimer l'utilisateur lui-même
    await db.execute(delete(User).where(User.id == uid))
    
    await db.commit()
    return {"status": "success", "message": "Compte supprimé avec succès"}
