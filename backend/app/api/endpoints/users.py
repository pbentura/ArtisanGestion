from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.user import UserReadWithSocietes, UserUpdate, UserPasswordUpdate
from app.core.security import get_password_hash, verify_password

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
    societes_dict = {s.id: s for s in user_data.societes}
    if user.societe_membre and user.societe_membre.id not in societes_dict:
        from app.schemas.societe import SocieteRead
        user_data.societes.append(SocieteRead.model_validate(user.societe_membre))
        
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
    societes_dict = {s.id: s for s in user_data.societes}
    if user.societe_membre and user.societe_membre.id not in societes_dict:
        from app.schemas.societe import SocieteRead
        user_data.societes.append(SocieteRead.model_validate(user.societe_membre))
        
    return user_data

@router.post("/me/switch-societe/{societe_id}", response_model=UserReadWithSocietes)
async def switch_societe(
    societe_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    from fastapi import HTTPException
    
    result = await db.execute(
        select(User).options(selectinload(User.societes), selectinload(User.societe_membre)).where(User.id == current_user.id)
    )
    user = result.scalars().first()
    
    is_target_owner = any(s.id == societe_id for s in user.societes)
    is_target_member = (user.societe_membre and user.societe_membre.id == societe_id)
    
    if not is_target_owner and not is_target_member:
        raise HTTPException(status_code=403, detail="Vous n'avez pas accès à cette société.")

    user.active_societe_id = societe_id
    db.add(user)
    await db.commit()
    
    result = await db.execute(
        select(User)
        .options(selectinload(User.societes), selectinload(User.societe_membre))
        .where(User.id == current_user.id)
    )
    reloaded_user = result.scalars().first()
    
    user_data = UserReadWithSocietes.model_validate(reloaded_user)
    societes_dict = {s.id: s for s in user_data.societes}
    if reloaded_user.societe_membre and reloaded_user.societe_membre.id not in societes_dict:
        from app.schemas.societe import SocieteRead
        user_data.societes.append(SocieteRead.model_validate(reloaded_user.societe_membre))
        
    return user_data


@router.put("/me/password")
async def update_password_me(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    password_data: UserPasswordUpdate,
) -> Any:
    """
    Définir ou modifier le mot de passe de l'utilisateur connecté.
    Si l'utilisateur a déjà un mot de passe, l'ancien mot de passe est obligatoire et vérifié.
    Si l'utilisateur n'a pas de mot de passe (compte Google), l'ancien mot de passe n'est pas requis.
    """
    if not password_data.new_password or len(password_data.new_password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Le nouveau mot de passe doit contenir au moins 6 caractères."
        )

    # Si l'utilisateur a déjà un mot de passe configuré
    if current_user.has_password:
        if not password_data.current_password:
            raise HTTPException(
                status_code=400,
                detail="Veuillez saisir votre mot de passe actuel."
            )
        if not verify_password(password_data.current_password, current_user.mdp):
            raise HTTPException(
                status_code=400,
                detail="Le mot de passe actuel est incorrect."
            )

    # Définir le nouveau mot de passe
    current_user.mdp = get_password_hash(password_data.new_password)
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    return {
        "status": "success",
        "message": "Mot de passe mis à jour avec succès",
        "has_password": True
    }


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

    if not is_owner and current_user.id_societe is not None:
        raise HTTPException(
            status_code=403,
            detail="En tant que collaborateur, vous ne pouvez pas supprimer votre compte. Veuillez contacter le propriétaire de l'entreprise."
        )

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


# ── Attribution de l'acquisition ──

class AttributionIn(BaseModel):
    """
    Provenance du premier contact, envoyée par le frontend après connexion.

    Le contenu vient du navigateur : on ne lui fait pas confiance sur la
    longueur (d'où max_length) et on ne s'en sert que pour du reporting
    interne, jamais pour accorder un droit.
    """
    model_config = ConfigDict(extra="ignore")

    utm_source: Optional[str] = Field(default=None, max_length=255)
    utm_medium: Optional[str] = Field(default=None, max_length=255)
    utm_campaign: Optional[str] = Field(default=None, max_length=255)
    utm_term: Optional[str] = Field(default=None, max_length=255)
    utm_content: Optional[str] = Field(default=None, max_length=255)
    gclid: Optional[str] = Field(default=None, max_length=255)
    landing_page: Optional[str] = Field(default=None, max_length=255)
    referrer: Optional[str] = Field(default=None, max_length=255)


CHAMPS_ATTRIBUTION = (
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "gclid",
    "landing_page",
    "referrer",
)


@router.post("/me/attribution", status_code=status.HTTP_204_NO_CONTENT)
async def enregistrer_attribution(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    attribution: AttributionIn,
):
    """
    Rattache au compte la campagne qui a amené l'artisan.

    Premier contact uniquement : si une provenance est déjà enregistrée, on
    renvoie 409 sans rien modifier. Sinon un artisan qui revient six mois plus
    tard par une autre annonce ferait disparaître la source qui l'a réellement
    converti.
    """
    if any(getattr(current_user, champ) for champ in CHAMPS_ATTRIBUTION):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La provenance de ce compte est déjà enregistrée.",
        )

    valeurs = attribution.model_dump(exclude_none=True)
    if not valeurs:
        return None

    for champ, valeur in valeurs.items():
        setattr(current_user, champ, valeur)

    db.add(current_user)
    await db.commit()
    return None
