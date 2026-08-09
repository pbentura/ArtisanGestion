import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_user, require_permission
from app.models.user import User
from app.models.societe import Societe
from app.models.invitation import Invitation
from app.schemas.invitation import (
    InvitationCreate,
    InvitationRead,
    InvitationPublicRead,
    CollaborateurRead,
    PermissionsUpdate,
)

router = APIRouter()


def _get_user_societe_id(user: User) -> int:
    """Retourne l'id de la société de l'utilisateur."""
    if user.id_societe:
        return user.id_societe
    if user.societes:
        return user.societes[0].id
    raise HTTPException(400, "Aucune entreprise associée.")


# ── Liste des collaborateurs ──

@router.get("/", response_model=List[CollaborateurRead])
async def list_collaborateurs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lister tous les membres de mon entreprise."""
    result = await db.execute(
        select(User).options(selectinload(User.societes)).where(User.id == current_user.id)
    )
    current_user = result.scalars().first()
    societe_id = _get_user_societe_id(current_user)

    # Le propriétaire
    result = await db.execute(
        select(User).join(Societe, Societe.id_user == User.id).where(Societe.id == societe_id)
    )
    owner = result.scalars().first()

    # Les collaborateurs
    result = await db.execute(
        select(User).where(User.id_societe == societe_id, User.is_owner == False)
    )
    collabs = result.scalars().all()

    membres = []
    if owner:
        membres.append(owner)
    membres.extend(collabs)
    return membres


# ── Invitations ──

@router.get("/invitations", response_model=List[InvitationRead])
async def list_invitations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lister les invitations de mon entreprise."""
    result = await db.execute(
        select(User).options(selectinload(User.societes)).where(User.id == current_user.id)
    )
    current_user = result.scalars().first()
    societe_id = _get_user_societe_id(current_user)

    result = await db.execute(
        select(Invitation)
        .where(Invitation.id_societe == societe_id)
        .order_by(Invitation.created_at.desc())
    )
    return result.scalars().all()


@router.post("/invite", response_model=InvitationRead)
async def create_invitation(
    body: InvitationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("can_invite")),
):
    """Créer une invitation (magic link) pour un collaborateur."""
    # Charger les sociétés
    result = await db.execute(
        select(User).options(selectinload(User.societes)).where(User.id == current_user.id)
    )
    current_user = result.scalars().first()
    
    # Vérifier l'abonnement TEAM
    if current_user.role not in ["TEAM", "ADMIN"]:
        raise HTTPException(
            status_code=403, 
            detail="Vous devez avoir l'abonnement Équipe pour inviter des collaborateurs."
        )

    societe_id = _get_user_societe_id(current_user)

    # Générer un token unique
    token = secrets.token_urlsafe(48)

    invitation = Invitation(
        id_societe=societe_id,
        invited_by=current_user.id,
        token=token,
        email=body.email,
        can_create_rapports=body.can_create_rapports,
        can_create_clients=body.can_create_clients,
        can_create_devis=body.can_create_devis,
        can_create_factures=body.can_create_factures,
        can_invite=body.can_invite,
        can_edit_societe=body.can_edit_societe,
        status="pending",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(invitation)
    await db.commit()
    await db.refresh(invitation)
    return invitation


@router.get("/invitation/{token}", response_model=InvitationPublicRead)
async def validate_invitation(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """Valider un token d'invitation (endpoint public, pas d'auth)."""
    result = await db.execute(
        select(Invitation).where(Invitation.token == token)
    )
    invitation = result.scalars().first()

    if not invitation:
        raise HTTPException(404, "Invitation introuvable.")

    if invitation.status != "pending":
        raise HTTPException(400, "Cette invitation a déjà été utilisée.")

    if invitation.expires_at < datetime.now(timezone.utc):
        invitation.status = "expired"
        await db.commit()
        raise HTTPException(400, "Cette invitation a expiré.")

    # Charger les infos de la société et de l'inviteur
    result = await db.execute(select(Societe).where(Societe.id == invitation.id_societe))
    societe = result.scalars().first()

    result = await db.execute(select(User).where(User.id == invitation.invited_by))
    inviter = result.scalars().first()

    return InvitationPublicRead(
        id=invitation.id,
        societe_nom=societe.nom if societe else "Entreprise",
        invited_by_name=f"{inviter.prenom} {inviter.nom}" if inviter else "Un collaborateur",
        email=invitation.email,
        can_create_rapports=invitation.can_create_rapports,
        can_create_clients=invitation.can_create_clients,
        can_create_devis=invitation.can_create_devis,
        can_create_factures=invitation.can_create_factures,
        can_invite=invitation.can_invite,
        can_edit_societe=invitation.can_edit_societe,
        status=invitation.status,
    )


@router.delete("/invitation/{invitation_id}")
async def cancel_invitation(
    invitation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Annuler une invitation en attente."""
    result = await db.execute(
        select(User).options(selectinload(User.societes)).where(User.id == current_user.id)
    )
    current_user = result.scalars().first()
    societe_id = _get_user_societe_id(current_user)

    result = await db.execute(
        select(Invitation).where(
            Invitation.id == invitation_id,
            Invitation.id_societe == societe_id,
        )
    )
    invitation = result.scalars().first()

    if not invitation:
        raise HTTPException(404, "Invitation introuvable.")

    await db.delete(invitation)
    await db.commit()
    return {"status": "success", "message": "Invitation annulée."}


# ── Gestion des permissions ──

@router.patch("/{user_id}/permissions", response_model=CollaborateurRead)
async def update_permissions(
    user_id: int,
    body: PermissionsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Modifier les permissions d'un collaborateur."""
    # Vérifier que c'est le propriétaire
    result = await db.execute(
        select(User).options(selectinload(User.societes)).where(User.id == current_user.id)
    )
    current_user = result.scalars().first()

    if not current_user.is_owner and not current_user.role == "ADMIN":
        raise HTTPException(403, "Seul le propriétaire peut modifier les permissions.")

    societe_id = _get_user_societe_id(current_user)

    # Récupérer le collaborateur
    result = await db.execute(
        select(User).where(User.id == user_id, User.id_societe == societe_id)
    )
    collab = result.scalars().first()

    if not collab:
        raise HTTPException(404, "Collaborateur introuvable.")

    if collab.is_owner:
        raise HTTPException(400, "Impossible de modifier les permissions du propriétaire.")

    # Appliquer les modifications
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(collab, field, value)

    db.add(collab)
    await db.commit()
    await db.refresh(collab)
    return collab


# ── Révoquer un collaborateur ──

@router.delete("/{user_id}")
async def remove_collaborateur(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Révoquer l'accès d'un collaborateur."""
    result = await db.execute(
        select(User).options(selectinload(User.societes)).where(User.id == current_user.id)
    )
    current_user = result.scalars().first()

    if not current_user.is_owner and not current_user.role == "ADMIN":
        raise HTTPException(403, "Seul le propriétaire peut révoquer un collaborateur.")

    societe_id = _get_user_societe_id(current_user)

    result = await db.execute(
        select(User).where(User.id == user_id, User.id_societe == societe_id)
    )
    collab = result.scalars().first()

    if not collab:
        raise HTTPException(404, "Collaborateur introuvable.")

    if collab.is_owner:
        raise HTTPException(400, "Impossible de révoquer le propriétaire.")

    # Transférer la propriété de ses documents au propriétaire de l'entreprise avant de le supprimer
    from sqlalchemy import update, delete
    from app.models.facture import Facture
    from app.models.devis import Devis
    from app.models.rapport import Rapport
    from app.models.client import Client

    soc_result = await db.execute(select(Societe).where(Societe.id == societe_id))
    societe = soc_result.scalars().first()
    
    if societe:
        owner_id = societe.id_user
        uid = collab.id
        await db.execute(update(Facture).where(Facture.id_user == uid).values(id_user=owner_id))
        await db.execute(update(Devis).where(Devis.id_user == uid).values(id_user=owner_id))
        await db.execute(update(Rapport).where(Rapport.id_user == uid).values(id_user=owner_id))
        await db.execute(update(Client).where(Client.id_user == uid).values(id_user=owner_id))

    await db.delete(collab)
    await db.commit()

    return {"status": "success", "message": "Compte collaborateur supprimé avec succès."}
