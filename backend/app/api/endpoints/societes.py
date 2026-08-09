from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Any

from app.api.deps import get_db, get_current_user, is_admin, get_user_societe_id, require_permission
from app.models.societe import Societe
from app.models.user import User
from app.schemas.societe import SocieteCreate, SocieteRead

router = APIRouter()

@router.get("/me", response_model=SocieteRead)
async def get_my_societe(
    db: AsyncSession = Depends(get_db),
    societe_id: int = Depends(get_user_societe_id),
) -> Any:
    """
    Récupérer la société de l'utilisateur connecté.
    """
    result = await db.execute(
        select(Societe).where(Societe.id == societe_id)
    )
    societe = result.scalars().first()
    
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
    current_user: User = Depends(require_permission("can_edit_societe")),
    societe_id: int = Depends(get_user_societe_id),
) -> Any:
    """
    Mettre à jour la société de l'utilisateur connecté.
    """
    result = await db.execute(
        select(Societe).where(Societe.id == societe_id)
    )
    societe = result.scalars().first()
    
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
    
    from app.core.websockets import manager
    await manager.broadcast_to_user(current_user.id, {
        "type": "SYNC_SOCIETE",
    })
    
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
    from app.core.config import settings
    import httpx
    
    if settings.ENVIRONMENT == "production" and current_user.role != "ADMIN":
        if not societe_in.siret:
            raise HTTPException(status_code=400, detail="Le SIRET est obligatoire en production.")
            
        async with httpx.AsyncClient() as client:
            res = await client.get(f"https://recherche-entreprises.api.gouv.fr/search?q={societe_in.siret}")
            if res.status_code != 200:
                raise HTTPException(status_code=400, detail="Erreur lors de la vérification du SIRET.")
            
            data = res.json()
            if not data.get("results") or len(data["results"]) == 0:
                raise HTTPException(status_code=400, detail="Ce SIRET est introuvable ou l'entreprise n'existe pas.")

    new_societe = Societe(
        id_user=current_user.id,
        **societe_in.model_dump()
    )
    db.add(new_societe)
    await db.commit()
    await db.refresh(new_societe)
    
    # Mettre à jour l'entreprise active de l'utilisateur
    current_user.id_societe = new_societe.id
    db.add(current_user)
    await db.commit()
    
    from app.core.websockets import manager
    await manager.broadcast_to_user(current_user.id, {
        "type": "SYNC_SOCIETE",
    })
    
    return new_societe

@router.delete("/me")
async def delete_my_societe(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    societe_id: int = Depends(get_user_societe_id),
) -> Any:
    """
    Supprimer la société active et toutes ses données associées (seulement si le compte est propriétaire et sans factures validées).
    """
    from sqlalchemy import delete, update
    from app.models.invitation import Invitation
    from app.models.client import Client
    from app.models.devis import Devis
    from app.models.facture import Facture
    from app.models.rapport import Rapport
    from app.models.ligne_facture import LigneFacture
    from app.models.ligne_devis import LigneDevis

    # 1. Vérifier que la société existe
    result = await db.execute(select(Societe).where(Societe.id == societe_id))
    societe = result.scalars().first()
    
    if not societe:
        raise HTTPException(status_code=404, detail="Société introuvable.")
        
    # 2. Vérifier que l'utilisateur est le propriétaire (c'est lui qui l'a créée)
    if societe.id_user != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Seul le propriétaire de l'entreprise peut la supprimer."
        )

    # 3. Conformité Légale : vérifier l'absence de factures validées/payées
    factures_validees_result = await db.execute(
        select(Facture.id).where(
            Facture.id_societe == societe_id,
            Facture.statut != "brouillon"
        ).limit(1)
    )
    has_valid_factures = factures_validees_result.scalars().first()
    if has_valid_factures:
        raise HTTPException(
            status_code=400,
            detail="Impossible de supprimer cette entreprise : des factures ont déjà été validées ou payées. Conformément à la loi anti-fraude à la TVA, ces documents comptables ne peuvent pas être détruits."
        )

    # --- SUPPRESSION EN CASCADE ---
    
    # 4. Détacher tous les collaborateurs de cette société
    await db.execute(
        update(User).where(User.id_societe == societe_id).values(id_societe=None, is_owner=False)
    )
    
    # 5. Supprimer les invitations en attente
    await db.execute(delete(Invitation).where(Invitation.id_societe == societe_id))

    # 6. Supprimer les factures brouillons et leurs lignes
    factures_result = await db.execute(select(Facture.id).where(Facture.id_societe == societe_id))
    factures_ids = factures_result.scalars().all()
    if factures_ids:
        await db.execute(delete(LigneFacture).where(LigneFacture.id_facture.in_(factures_ids)))
        await db.execute(delete(Facture).where(Facture.id_societe == societe_id))
        
    # 7. Supprimer les devis et leurs lignes
    devis_result = await db.execute(select(Devis.id).where(Devis.id_societe == societe_id))
    devis_ids = devis_result.scalars().all()
    if devis_ids:
        await db.execute(delete(LigneDevis).where(LigneDevis.id_devis.in_(devis_ids)))
        await db.execute(delete(Devis).where(Devis.id_societe == societe_id))

    # 8. Supprimer les autres documents
    await db.execute(delete(Rapport).where(Rapport.id_societe == societe_id))
    await db.execute(delete(Client).where(Client.id_societe == societe_id))
    
    # 9. Supprimer la société elle-même
    await db.execute(delete(Societe).where(Societe.id == societe_id))

    # 10. Re-assigner l'utilisateur actif à une autre société s'il en a une
    result_autres = await db.execute(
        select(Societe).where(Societe.id_user == current_user.id).order_by(Societe.id.desc())
    )
    autre_societe = result_autres.scalars().first()
    
    current_user.id_societe = autre_societe.id if autre_societe else None
    current_user.is_owner = bool(autre_societe)
    db.add(current_user)

    await db.commit()
    
    from app.core.websockets import manager
    await manager.broadcast_to_user(current_user.id, {
        "type": "SYNC_SOCIETE",
    })

    return {"status": "success", "message": "Entreprise supprimée avec succès."}
