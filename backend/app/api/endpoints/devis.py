import logging
from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.api import deps
from app.core.config import settings
from app.core.rate_limit import limiter
from app.models.devis import Devis
from app.models.rapport import Rapport
from app.models.client import Client
from app.models.societe import Societe
from app.models.user import User
from app.schemas.devis import (
    Devis as DevisSchema,
    DevisCreate,
    DevisUpdate,
    DemandeSignature,
    DevisPublic,
    LienSignature,
    SignatureSoumise,
    SocieteSignature,
)
from app.models.ligne_devis import LigneDevis
from app.services import signature as sig
from app.services.email_service import send_signature_request, send_signature_confirmation

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("", response_model=List[DevisSchema])
async def read_devis(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(deps.get_db),
    societe_id: int = Depends(deps.get_user_societe_id)
):
    """
    Récupère la liste des devis de l'utilisateur connecté.
    """
    result = await db.execute(
        select(Devis)
        .options(joinedload(Devis.client), joinedload(Devis.lignes))
        .where(Devis.id_societe == societe_id)
        .offset(skip)
        .limit(limit)
    )
    return result.unique().scalars().all()

@router.post("", response_model=DevisSchema)
async def create_devis(
    devis_in: DevisCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.require_permission("can_create_devis")),
    societe_id: int = Depends(deps.get_user_societe_id),
    _: User = Depends(deps.check_trial_active)
):
    """
    Crée un nouveau devis pour l'utilisateur connecté.
    """
    client_result = await db.execute(
        select(Client).where(Client.id == devis_in.id_client, Client.id_societe == societe_id)
    )
    client_obj = client_result.scalars().first()
    if not client_obj:
        raise HTTPException(status_code=400, detail="Client invalide ou non autorisé")
        
    devis_data = devis_in.model_dump(exclude={"lignes"})
    db_devis = Devis(**devis_data, id_user=current_user.id, id_societe=societe_id)
    
    if devis_in.lignes:
        for ligne_in in devis_in.lignes:
            ligne_data = ligne_in.model_dump()
            db_ligne = LigneDevis(**ligne_data)
            db_devis.lignes.append(db_ligne)

    db.add(db_devis)
    await db.commit()
    
    # Reload fully mapped object with relationships to avoid MissingGreenlet on Pydantic serialization
    result = await db.execute(
        select(Devis)
        .options(joinedload(Devis.client), joinedload(Devis.lignes))
        .where(Devis.id == db_devis.id)
    )
    db_devis_loaded = result.unique().scalars().first()
    return db_devis_loaded

from app.schemas.ligne_devis import LigneDevis as LigneDevisSchema

@router.get("/lignes/descriptions", response_model=List[LigneDevisSchema])
async def get_lignes_descriptions(
    db: AsyncSession = Depends(deps.get_db),
    societe_id: int = Depends(deps.get_user_societe_id)
):
    """
    Récupère la liste des lignes complètes uniques (groupées par description) 
    pour proposer l'autocomplétion avancée.
    """
    result = await db.execute(
        select(LigneDevis)
        .join(Devis, LigneDevis.id_devis == Devis.id)
        .where(Devis.id_societe == societe_id)
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

@router.get("/{devis_id}", response_model=DevisSchema)
async def read_un_devis(
    devis_id: int,
    db: AsyncSession = Depends(deps.get_db),
    societe_id: int = Depends(deps.get_user_societe_id)
):
    """
    Récupère un devis spécifique.
    """
    result = await db.execute(
        select(Devis)
        .options(joinedload(Devis.client), joinedload(Devis.lignes))
        .where(Devis.id == devis_id, Devis.id_societe == societe_id)
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
    current_user: User = Depends(deps.require_permission("can_create_devis")),
    societe_id: int = Depends(deps.get_user_societe_id)
):
    """
    Met à jour un devis existant (infos générales uniquement).
    """
    result = await db.execute(
        select(Devis)
        .options(joinedload(Devis.client), joinedload(Devis.lignes))
        .where(Devis.id == devis_id, Devis.id_societe == societe_id)
    )
    db_devis = result.unique().scalars().first()
    
    if not db_devis:
        raise HTTPException(status_code=404, detail="Devis non trouvé")
        
    if devis_in.id_client is not None and devis_in.id_client != db_devis.id_client:
        client_result = await db.execute(
            select(Client).where(Client.id == devis_in.id_client, Client.id_societe == societe_id)
        )
        new_client = client_result.scalars().first()
        if not new_client:
            raise HTTPException(status_code=400, detail="Client invalide ou non autorisé")
        db_devis.client = new_client

    update_data = devis_in.model_dump(exclude_unset=True)
    
    # Trial restriction: if trial ended, only allow statut updates
    if deps.get_trial_days_remaining(current_user) == 0:
        forbidden_fields = set(update_data.keys()) - {"statut"}
        if forbidden_fields:
            raise HTTPException(
                status_code=403,
                detail="Votre période d'essai est terminée. Seul le changement de statut est autorisé."
            )

    for field, value in update_data.items():
        if field == "id_rapport":
            continue
        setattr(db_devis, field, value)
    
    await db.commit()
    
    # Reload fully mapped object with relationships to avoid MissingGreenlet
    reload_result = await db.execute(
        select(Devis)
        .options(joinedload(Devis.client), joinedload(Devis.lignes))
        .where(Devis.id == db_devis.id)
    )
    return reload_result.unique().scalars().first()

@router.delete("/{devis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_devis(
    devis_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.require_permission("can_create_devis")),
    societe_id: int = Depends(deps.get_user_societe_id)
):
    """
    Supprime un devis.
    """
    result = await db.execute(
        select(Devis).where(Devis.id == devis_id, Devis.id_societe == societe_id)
    )
    db_devis = result.scalars().first()
    
    if not db_devis:
        raise HTTPException(status_code=404, detail="Devis non trouvé")
        
    await db.delete(db_devis)
    await db.commit()
    return None


# ===========================================================================
# Signature électronique à distance
# ===========================================================================

@router.post("/{devis_id}/demande-signature", response_model=LienSignature)
async def demander_signature(
    devis_id: int,
    corps: DemandeSignature,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.require_permission("can_create_devis")),
    societe_id: int = Depends(deps.get_user_societe_id),
    _: User = Depends(deps.check_trial_active),
):
    """
    Génère un lien de signature et l'envoie au client par email.

    Régénérer un lien invalide le précédent : le jeton est remplacé.
    """
    result = await db.execute(
        select(Devis)
        .options(joinedload(Devis.client), joinedload(Devis.lignes))
        .where(Devis.id == devis_id, Devis.id_societe == societe_id)
    )
    devis = result.unique().scalars().first()
    if not devis:
        raise HTTPException(status_code=404, detail="Devis non trouvé")

    if devis.signature_le:
        raise HTTPException(status_code=400, detail="Ce devis est déjà signé.")

    if devis.statut == "facturé":
        raise HTTPException(status_code=400, detail="Ce devis a déjà été facturé.")

    destinataire = (corps.email_client or "").strip() or (devis.client.email or "").strip()
    if not destinataire:
        raise HTTPException(
            status_code=400,
            detail="Aucune adresse email pour ce client. Renseignez-la dans sa fiche.",
        )

    societe_result = await db.execute(select(Societe).where(Societe.id == societe_id))
    societe = societe_result.scalars().first()
    if not societe:
        raise HTTPException(status_code=400, detail="Entreprise introuvable.")

    devis.signature_token = sig.generer_token()
    devis.signature_token_expire_le = datetime.now(timezone.utc) + timedelta(
        days=sig.VALIDITE_LIEN_JOURS
    )
    # Le devis part chez le client : il n'est plus un brouillon.
    if devis.statut == "brouillon":
        devis.statut = "envoyé"

    await db.commit()
    await db.refresh(devis)

    envoye = await send_signature_request(
        to=destinataire,
        client_nom=devis.client.nom if devis.client else "",
        artisan_nom=societe.nom,
        artisan_email=societe.email or "",
        numero_devis=devis.numero_devis,
        montant_ttc=f"{devis.total_ttc:.2f}",
        objet=devis.objet_devis or "",
        token=devis.signature_token,
        jours_validite=sig.VALIDITE_LIEN_JOURS,
    )

    return LienSignature(
        url=f"{(settings.FRONTEND_URL or '').rstrip('/')}/signer/{devis.signature_token}",
        expire_le=devis.signature_token_expire_le,
        email_envoye_a=destinataire if envoye else None,
    )


@router.delete("/{devis_id}/demande-signature", status_code=status.HTTP_204_NO_CONTENT)
async def annuler_demande_signature(
    devis_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.require_permission("can_create_devis")),
    societe_id: int = Depends(deps.get_user_societe_id),
):
    """Invalide le lien de signature en cours (le devis signé reste intact)."""
    result = await db.execute(
        select(Devis).where(Devis.id == devis_id, Devis.id_societe == societe_id)
    )
    devis = result.scalars().first()
    if not devis:
        raise HTTPException(status_code=404, detail="Devis non trouvé")
    if devis.signature_le:
        raise HTTPException(
            status_code=400, detail="Ce devis est signé : le lien ne peut plus être annulé."
        )

    devis.signature_token = None
    devis.signature_token_expire_le = None
    await db.commit()
    return None


async def _charger_devis_par_token(db: AsyncSession, token: str) -> Devis:
    """Charge un devis depuis son jeton public, en validant expiration et état."""
    result = await db.execute(
        select(Devis)
        .options(
            joinedload(Devis.client),
            joinedload(Devis.lignes),
            joinedload(Devis.societe),
        )
        .where(Devis.signature_token == token)
    )
    devis = result.unique().scalars().first()

    if not devis:
        raise HTTPException(status_code=404, detail="Ce lien de signature est invalide.")

    if devis.signature_token_expire_le:
        expire = devis.signature_token_expire_le
        if expire.tzinfo is None:
            expire = expire.replace(tzinfo=timezone.utc)
        if expire < datetime.now(timezone.utc) and not devis.signature_le:
            raise HTTPException(
                status_code=410,
                detail="Ce lien de signature a expiré. Demandez-en un nouveau à votre artisan.",
            )

    return devis


@router.get("/public/{token}", response_model=DevisPublic)
@limiter.limit("60/hour")
async def consulter_devis_public(
    request: Request,
    token: str,
    db: AsyncSession = Depends(deps.get_db),
):
    """
    Devis consultable sans compte par le détenteur du lien.
    Ne renvoie que ce qui est nécessaire à la lecture et à la signature.
    """
    devis = await _charger_devis_par_token(db, token)
    societe = devis.societe

    return DevisPublic(
        numero_devis=devis.numero_devis,
        date_devis=devis.date_devis,
        objet_devis=devis.objet_devis,
        titre_document_pdf=devis.titre_document_pdf,
        sous_total_ht=devis.sous_total_ht,
        total_tva=devis.total_tva,
        total_ttc=devis.total_ttc,
        nb_jours_validite=devis.nb_jours_validite,
        conditions_particulieres=devis.conditions_particulieres,
        lignes=list(devis.lignes),
        client_nom=devis.client.nom if devis.client else "",
        societe=SocieteSignature(
            nom=societe.nom if societe else "",
            logo=societe.logo if societe else None,
            adresse=societe.adresse if societe else None,
            code_postal=societe.code_postal if societe else None,
            ville=societe.ville if societe else None,
            telephone=societe.telephone if societe else None,
            email=societe.email if societe else None,
            siret=societe.siret if societe else None,
            couleur_document=societe.couleur_document if societe else None,
        ),
        deja_signe=bool(devis.signature_le),
        signature_nom=devis.signature_nom,
        signature_le=devis.signature_le,
    )


@router.post("/public/{token}/signer", response_model=DevisPublic)
@limiter.limit("10/hour")
async def signer_devis_public(
    request: Request,
    token: str,
    soumission: SignatureSoumise,
    db: AsyncSession = Depends(deps.get_db),
):
    """
    Enregistre la signature du client et consigne les éléments de preuve.
    Idempotent : un devis déjà signé n'est jamais réécrit.
    """
    devis = await _charger_devis_par_token(db, token)

    if devis.signature_le:
        raise HTTPException(status_code=409, detail="Ce devis a déjà été signé.")

    if not soumission.accepte_conditions:
        raise HTTPException(
            status_code=400,
            detail="Vous devez accepter les conditions du devis pour le signer.",
        )

    nom = (soumission.nom_signataire or "").strip()
    if len(nom) < 2:
        raise HTTPException(status_code=400, detail="Merci d'indiquer votre nom complet.")

    if not sig.signature_valide(soumission.signature):
        raise HTTPException(
            status_code=400, detail="La signature est vide ou illisible. Merci de recommencer."
        )

    devis.signature = soumission.signature
    devis.signature_nom = nom[:255]
    devis.signature_email = (soumission.email_signataire or "").strip()[:255] or None
    devis.signature_le = datetime.now(timezone.utc)
    devis.signature_ip = sig.adresse_client(request)
    devis.signature_user_agent = (request.headers.get("user-agent") or "")[:500]
    devis.signature_empreinte = sig.calculer_empreinte(devis, list(devis.lignes))
    devis.statut = "accepté"
    # Le lien a rempli son office : on le neutralise.
    devis.signature_token = None
    devis.signature_token_expire_le = None

    await db.commit()
    await db.refresh(devis)

    # Prévenir l'artisan — sans faire échouer la signature si l'email tombe.
    try:
        proprietaire = await db.execute(select(User).where(User.id == devis.id_user))
        user = proprietaire.scalars().first()
        if user and user.email:
            await send_signature_confirmation(
                to=user.email,
                artisan_nom=user.prenom or "",
                client_nom=devis.client.nom if devis.client else "",
                numero_devis=devis.numero_devis,
                signataire=nom,
            )
        if user:
            from app.core.websockets import manager
            await manager.broadcast_to_user(user.id, {
                "type": "DEVIS_SIGNE",
                "devis_id": devis.id,
                "numero": devis.numero_devis,
                "signataire": nom,
            })
    except Exception as e:
        logger.warning("Notification de signature non délivrée pour %s : %s", devis.numero_devis, e)

    societe = devis.societe
    return DevisPublic(
        numero_devis=devis.numero_devis,
        date_devis=devis.date_devis,
        objet_devis=devis.objet_devis,
        titre_document_pdf=devis.titre_document_pdf,
        sous_total_ht=devis.sous_total_ht,
        total_tva=devis.total_tva,
        total_ttc=devis.total_ttc,
        nb_jours_validite=devis.nb_jours_validite,
        conditions_particulieres=devis.conditions_particulieres,
        lignes=list(devis.lignes),
        client_nom=devis.client.nom if devis.client else "",
        societe=SocieteSignature(
            nom=societe.nom if societe else "",
            logo=societe.logo if societe else None,
            adresse=societe.adresse if societe else None,
            code_postal=societe.code_postal if societe else None,
            ville=societe.ville if societe else None,
            telephone=societe.telephone if societe else None,
            email=societe.email if societe else None,
            siret=societe.siret if societe else None,
            couleur_document=societe.couleur_document if societe else None,
        ),
        deja_signe=True,
        signature_nom=devis.signature_nom,
        signature_le=devis.signature_le,
    )
