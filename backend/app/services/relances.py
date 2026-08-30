"""
Relances automatiques des factures impayées.

Le service parcourt les factures échues et non réglées, puis envoie une relance
par palier de retard. Deux garde-fous encadrent l'envoi :

- l'idempotence est portée par la base (contrainte unique facture+niveau), pas
  par le calendrier : rejouer la tâche n'envoie jamais deux fois le même palier ;
- seul un palier est envoyé par facture et par exécution, pour qu'un impayé
  ancien découvert tardivement ne déclenche pas trois emails d'affilée.

Réservé au plan Équipe, comme annoncé sur la page de tarifs.
"""

import logging
from datetime import date, datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models.facture import Facture
from app.models.relance import RelanceFacture
from app.models.societe import Societe
from app.models.user import User
from app.services.email_service import send_relance_facture

logger = logging.getLogger(__name__)

# Rôles autorisant les relances automatiques.
ROLES_AUTORISES = {"TEAM", "ADMIN"}


def paliers(societe: Societe) -> List[int]:
    """
    Jours de retard déclenchant chaque relance, lus depuis la société.
    Retombe sur 3/10/21 si la valeur stockée est inexploitable.
    """
    brut = (societe.relances_jours or "").strip()
    try:
        valeurs = sorted({int(p) for p in brut.split(",") if p.strip()})
        valeurs = [v for v in valeurs if 0 < v <= 365]
    except ValueError:
        valeurs = []
    return valeurs or [3, 10, 21]


def niveau_attendu(jours_de_retard: int, seuils: List[int]) -> int:
    """Palier le plus élevé atteint pour un retard donné (0 = aucun)."""
    niveau = 0
    for i, seuil in enumerate(seuils, start=1):
        if jours_de_retard >= seuil:
            niveau = i
    return niveau


async def factures_a_relancer(db: AsyncSession, societe_id: Optional[int] = None) -> List[Facture]:
    """
    Factures validées, non payées, non avoir, dont l'échéance est dépassée.
    Les acomptes sont inclus : ils sont exigibles comme les autres.
    """
    requete = (
        select(Facture)
        .options(
            joinedload(Facture.client),
            joinedload(Facture.societe),
            selectinload(Facture.relances),
        )
        .where(
            Facture.statut == "validée",
            Facture.est_payee.is_(False),
            Facture.est_avoir.is_(False),
            Facture.date_echeance.isnot(None),
            Facture.date_echeance < date.today(),
        )
    )
    if societe_id is not None:
        requete = requete.where(Facture.id_societe == societe_id)

    result = await db.execute(requete)
    return list(result.unique().scalars().all())


async def _proprietaire_autorise(db: AsyncSession, societe: Societe) -> Optional[User]:
    """Retourne le propriétaire de la société s'il a le plan requis."""
    if not societe or not societe.id_user:
        return None
    result = await db.execute(select(User).where(User.id == societe.id_user))
    user = result.scalars().first()
    if not user or (user.role or "USER") not in ROLES_AUTORISES:
        return None
    return user


async def envoyer_relance(
    db: AsyncSession,
    facture: Facture,
    niveau: int,
    jours_de_retard: int,
    automatique: bool = True,
) -> bool:
    """
    Envoie une relance et l'enregistre.

    La trace est insérée *avant* l'envoi : en cas de plantage après l'appel à
    Resend, on préfère une relance manquante à une relance envoyée deux fois.
    Retourne False si le palier a déjà été traité.
    """
    destinataire = (facture.client.email or "").strip() if facture.client else ""
    if not destinataire:
        logger.info(
            "Facture %s : relance impossible, le client n'a pas d'email.", facture.numero_facture
        )
        return False

    trace = RelanceFacture(
        id_facture=facture.id,
        niveau=niveau,
        jours_de_retard=jours_de_retard,
        destinataire=destinataire,
        automatique=automatique,
    )
    db.add(trace)
    try:
        await db.commit()
    except IntegrityError:
        # La contrainte unique a joué : ce palier est déjà parti.
        await db.rollback()
        logger.debug(
            "Facture %s : relance niveau %s déjà enregistrée.", facture.numero_facture, niveau
        )
        return False

    societe = facture.societe
    await send_relance_facture(
        to=destinataire,
        client_nom=facture.client.nom if facture.client else "",
        artisan_nom=societe.nom if societe else "",
        artisan_email=(societe.email if societe else "") or "",
        numero_facture=facture.numero_facture,
        montant_ttc=f"{facture.total_ttc:.2f}",
        date_echeance=facture.date_echeance.strftime("%d/%m/%Y") if facture.date_echeance else "",
        jours_de_retard=jours_de_retard,
        niveau=niveau,
        payment_url=facture.stripe_payment_url,
    )
    return True


async def traiter_relances(db: AsyncSession, societe_id: Optional[int] = None) -> dict:
    """
    Passe en revue les impayés et envoie les relances dues.
    Retourne un compte rendu exploitable dans les logs comme dans les tests.
    """
    bilan = {"examinees": 0, "envoyees": 0, "ignorees": 0}
    autorisations: dict = {}

    for facture in await factures_a_relancer(db, societe_id):
        bilan["examinees"] += 1
        societe = facture.societe

        if not societe or not societe.relances_actives:
            bilan["ignorees"] += 1
            continue

        # Le plan est vérifié une fois par société, pas par facture.
        if societe.id not in autorisations:
            autorisations[societe.id] = await _proprietaire_autorise(db, societe) is not None
        if not autorisations[societe.id]:
            bilan["ignorees"] += 1
            continue

        jours = (date.today() - facture.date_echeance).days
        attendu = niveau_attendu(jours, paliers(societe))
        if attendu == 0:
            bilan["ignorees"] += 1
            continue

        deja_envoyes = {r.niveau for r in facture.relances}
        # On ne rattrape pas l'historique : seul le prochain palier non traité part.
        a_envoyer = next((n for n in range(1, attendu + 1) if n not in deja_envoyes), None)
        if a_envoyer is None:
            bilan["ignorees"] += 1
            continue

        if await envoyer_relance(db, facture, a_envoyer, jours, automatique=True):
            bilan["envoyees"] += 1
        else:
            bilan["ignorees"] += 1

    logger.info(
        "Relances : %s facture(s) examinée(s), %s envoyée(s), %s ignorée(s).",
        bilan["examinees"], bilan["envoyees"], bilan["ignorees"],
    )
    return bilan


async def executer_tache_quotidienne() -> dict:
    """Point d'entrée de la tâche planifiée : ouvre sa propre session."""
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        try:
            return await traiter_relances(db)
        except Exception:
            logger.exception("La tâche de relances a échoué.")
            return {"examinees": 0, "envoyees": 0, "ignorees": 0, "erreur": True}
