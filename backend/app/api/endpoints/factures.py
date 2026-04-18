from typing import List
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.api import deps
from app.models.facture import Facture
from app.models.ligne_facture import LigneFacture
from app.models.client import Client
from app.models.user import User
from app.models.devis import Devis
from app.models.ligne_devis import LigneDevis
from app.schemas.facture import (
    Facture as FactureSchema,
    FactureCreate,
    FactureUpdate,
    FactureCreateFromDevis,
)

router = APIRouter()


@router.get("", response_model=List[FactureSchema])
async def read_factures(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Récupère la liste des factures de l'utilisateur connecté.
    """
    result = await db.execute(
        select(Facture)
        .options(joinedload(Facture.client), joinedload(Facture.lignes))
        .where(Facture.id_user == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    return result.unique().scalars().all()


@router.post("", response_model=FactureSchema)
async def create_facture(
    facture_in: FactureCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Crée une nouvelle facture pour l'utilisateur connecté.
    """
    # Vérifier le client
    client_result = await db.execute(
        select(Client).where(
            Client.id == facture_in.id_client, Client.id_user == current_user.id
        )
    )
    client_obj = client_result.scalars().first()
    if not client_obj:
        raise HTTPException(status_code=400, detail="Client invalide ou non autorisé")

    facture_data = facture_in.model_dump(exclude={"lignes"})

    # Calculer la date d'échéance si non fournie
    if not facture_data.get("date_echeance"):
        facture_data["date_echeance"] = facture_data["date_facture"] + timedelta(
            days=facture_data.get("nb_jours_echeance", 30)
        )

    db_facture = Facture(**facture_data, id_user=current_user.id)

    if facture_in.lignes:
        for ligne_in in facture_in.lignes:
            ligne_data = ligne_in.model_dump()
            db_ligne = LigneFacture(**ligne_data)
            db_facture.lignes.append(db_ligne)

    db.add(db_facture)
    await db.commit()

    # Reload fully mapped object with relationships
    result = await db.execute(
        select(Facture)
        .options(joinedload(Facture.client), joinedload(Facture.lignes))
        .where(Facture.id == db_facture.id)
    )
    db_facture_loaded = result.unique().scalars().first()
    return db_facture_loaded


@router.post("/from-devis/{devis_id}", response_model=FactureSchema)
async def create_facture_from_devis(
    devis_id: int,
    facture_in: FactureCreateFromDevis,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Crée une facture à partir d'un devis existant.
    Copie automatiquement les lignes et informations du devis.
    """
    # Charger le devis avec ses lignes
    result = await db.execute(
        select(Devis)
        .options(joinedload(Devis.lignes), joinedload(Devis.client))
        .where(Devis.id == devis_id, Devis.id_user == current_user.id)
    )
    db_devis = result.unique().scalars().first()
    if not db_devis:
        raise HTTPException(status_code=404, detail="Devis non trouvé")

    # Générer les valeurs par défaut
    now = date.today()
    date_facture = facture_in.date_facture or now
    numero_facture = facture_in.numero_facture or f"FAC-{now.strftime('%Y%m%d')}-{now.strftime('%H%M')}"

    date_echeance = date_facture + timedelta(days=facture_in.nb_jours_echeance)

    db_facture = Facture(
        date_facture=date_facture,
        numero_facture=numero_facture,
        titre_document_pdf=facture_in.titre_document_pdf,
        objet_facture=db_devis.objet_devis,
        sous_total_ht=db_devis.sous_total_ht,
        total_tva=db_devis.total_tva,
        total_ttc=db_devis.total_ttc,
        nb_jours_echeance=facture_in.nb_jours_echeance,
        date_echeance=date_echeance,
        statut=facture_in.statut,
        est_payee=False,
        conditions_particulieres=facture_in.conditions_particulieres or db_devis.conditions_particulieres,
        id_client=db_devis.id_client,
        id_user=current_user.id,
        id_devis=db_devis.id,
    )

    # Copier les lignes du devis
    for ligne_devis in db_devis.lignes:
        db_ligne = LigneFacture(
            description=ligne_devis.description,
            quantite=ligne_devis.quantite,
            prix_unite_ht=ligne_devis.prix_unite_ht,
            taux_tva=ligne_devis.taux_tva,
            total_ht=ligne_devis.total_ht,
        )
        db_facture.lignes.append(db_ligne)

    db.add(db_facture)
    await db.commit()

    # Reload
    result = await db.execute(
        select(Facture)
        .options(joinedload(Facture.client), joinedload(Facture.lignes))
        .where(Facture.id == db_facture.id)
    )
    db_facture_loaded = result.unique().scalars().first()
    return db_facture_loaded


@router.get("/{facture_id}", response_model=FactureSchema)
async def read_une_facture(
    facture_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Récupère une facture spécifique.
    """
    result = await db.execute(
        select(Facture)
        .options(joinedload(Facture.client), joinedload(Facture.lignes))
        .where(Facture.id == facture_id, Facture.id_user == current_user.id)
    )
    facture = result.unique().scalars().first()
    if not facture:
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    return facture


@router.put("/{facture_id}", response_model=FactureSchema)
async def update_facture(
    facture_id: int,
    facture_in: FactureUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Met à jour une facture existante (infos générales uniquement).
    """
    result = await db.execute(
        select(Facture)
        .options(joinedload(Facture.client), joinedload(Facture.lignes))
        .where(Facture.id == facture_id, Facture.id_user == current_user.id)
    )
    db_facture = result.unique().scalars().first()

    if not db_facture:
        raise HTTPException(status_code=404, detail="Facture non trouvée")

    # Une facture validée ne peut plus être modifiée (sauf le champ est_payee)
    update_data = facture_in.model_dump(exclude_unset=True)
    if db_facture.statut == "validée":
        allowed_fields = {"est_payee"}
        forbidden_fields = set(update_data.keys()) - allowed_fields
        if forbidden_fields:
            raise HTTPException(
                status_code=403,
                detail="Une facture validée ne peut plus être modifiée. Seul le statut de paiement peut être changé."
            )

    if facture_in.id_client is not None and facture_in.id_client != db_facture.id_client:
        client_result = await db.execute(
            select(Client).where(
                Client.id == facture_in.id_client, Client.id_user == current_user.id
            )
        )
        new_client = client_result.scalars().first()
        if not new_client:
            raise HTTPException(status_code=400, detail="Client invalide ou non autorisé")
        db_facture.client = new_client

    for field, value in update_data.items():
        setattr(db_facture, field, value)

    await db.commit()
    await db.refresh(db_facture)
    return db_facture


@router.delete("/{facture_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_facture(
    facture_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Supprime une facture.
    """
    result = await db.execute(
        select(Facture).where(
            Facture.id == facture_id, Facture.id_user == current_user.id
        )
    )
    db_facture = result.scalars().first()

    if not db_facture:
        raise HTTPException(status_code=404, detail="Facture non trouvée")

    await db.delete(db_facture)
    await db.commit()
    return None
