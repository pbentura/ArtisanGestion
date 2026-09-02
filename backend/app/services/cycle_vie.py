"""
Accompagnement de la période d'essai.

Un artisan qui s'inscrit et que personne ne relance disparaît. C'est la fuite
la plus coûteuse quand l'acquisition est payante : le clic est facturé, le
compte est créé, et il ne se passe plus rien pendant quatorze jours.

Trois messages, envoyés au plus une fois chacun :

- ``activation``  : inscrit depuis 2 jours, aucun document créé ;
- ``essai_j3``    : il reste 3 jours d'essai ;
- ``essai_termine`` : l'essai vient de se terminer.

Comme pour les relances de factures, l'idempotence est portée par la base
(contrainte unique utilisateur+type) et non par le calendrier : rejouer la
tâche, la rattraper après une panne ou l'exécuter depuis deux processus
n'envoie jamais deux fois le même message.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.devis import Devis
from app.models.email_cycle_vie import EmailCycleVie
from app.models.facture import Facture
from app.models.rapport import Rapport
from app.models.user import User
from app.services.email_service import (
    send_activation_reminder,
    send_trial_ended,
    send_trial_ending_soon,
)

logger = logging.getLogger(__name__)

DUREE_ESSAI_JOURS = 14

TYPE_ACTIVATION = "activation"
TYPE_ESSAI_J3 = "essai_j3"
TYPE_ESSAI_TERMINE = "essai_termine"

# Un artisan qui vient de s'inscrire n'a pas à être relancé le lendemain :
# on lui laisse le temps de revenir de lui-même.
JOURS_AVANT_RELANCE_ACTIVATION = 2

# Nombre de jours d'essai restants déclenchant l'avertissement.
JOURS_AVANT_FIN = 3

# Seuls les comptes sans abonnement sont concernés.
ROLES_SANS_ABONNEMENT = ("USER", None)

# Filet de sécurité : on ne réveille pas d'anciens comptes inactifs depuis des
# mois si la tâche n'a pas tourné pendant longtemps.
FENETRE_RATTRAPAGE_JOURS = 7


def _aware(valeur: datetime) -> datetime:
    """Les dates lues en base peuvent être naïves selon le pilote."""
    return valeur if valeur.tzinfo else valeur.replace(tzinfo=timezone.utc)


def jours_depuis_inscription(user: User, maintenant: Optional[datetime] = None) -> Optional[int]:
    if not user.date_inscription:
        return None
    maintenant = maintenant or datetime.now(timezone.utc)
    return (maintenant - _aware(user.date_inscription)).days


async def _a_cree_un_document(db: AsyncSession, user_id: int) -> bool:
    """Vrai dès qu'un rapport, un devis ou une facture existe pour ce compte."""
    for modele in (Rapport, Devis, Facture):
        result = await db.execute(
            select(modele.id).where(modele.id_user == user_id).limit(1)
        )
        if result.scalar() is not None:
            return True
    return False


async def _candidats(db: AsyncSession) -> List[User]:
    """
    Comptes encore en essai, ou tout juste sortis, et sans abonnement.

    Les comptes non vérifiés sont exclus : ils n'ont jamais pu se connecter,
    les relancer sur l'usage du produit n'aurait aucun sens.
    """
    plancher = datetime.now(timezone.utc) - timedelta(
        days=DUREE_ESSAI_JOURS + FENETRE_RATTRAPAGE_JOURS
    )
    result = await db.execute(
        select(User).where(
            or_(User.role.in_(("USER",)), User.role.is_(None)),
            User.is_email_verified.is_(True),
            User.date_inscription.isnot(None),
            User.date_inscription >= plancher,
        )
    )
    return list(result.scalars().all())


async def _deja_envoyes(db: AsyncSession, user_ids: List[int]) -> dict:
    """Types d'emails déjà partis, par utilisateur, en une seule requête."""
    if not user_ids:
        return {}
    result = await db.execute(
        select(EmailCycleVie.id_user, EmailCycleVie.type).where(
            EmailCycleVie.id_user.in_(user_ids)
        )
    )
    envoyes: dict = {}
    for id_user, type_ in result.all():
        envoyes.setdefault(id_user, set()).add(type_)
    return envoyes


async def _marquer_puis_envoyer(db: AsyncSession, user: User, type_: str, envoi) -> bool:
    """
    Enregistre la trace *avant* l'envoi, puis envoie.

    Dans cet ordre, un plantage après l'appel à Resend laisse un email
    manquant plutôt qu'un doublon — c'est le compromis retenu pour les
    relances de factures, et il vaut aussi ici : mieux vaut oublier un message
    que harceler un artisan.
    """
    db.add(EmailCycleVie(id_user=user.id, type=type_))
    try:
        await db.commit()
    except IntegrityError:
        # La contrainte unique a joué : un autre processus est passé avant.
        await db.rollback()
        return False

    await envoi()
    return True


async def traiter_cycle_vie(db: AsyncSession) -> dict:
    """Parcourt les comptes en essai et envoie les messages dus."""
    bilan = {"examines": 0, "activation": 0, "essai_j3": 0, "essai_termine": 0}

    candidats = await _candidats(db)
    envoyes = await _deja_envoyes(db, [u.id for u in candidats])
    maintenant = datetime.now(timezone.utc)

    for user in candidats:
        bilan["examines"] += 1
        deja = envoyes.get(user.id, set())
        anciennete = jours_depuis_inscription(user, maintenant)
        if anciennete is None:
            continue

        restants = DUREE_ESSAI_JOURS - anciennete
        prenom = user.prenom or ""

        # Un seul message par compte et par exécution : découvrir un compte
        # tardivement ne doit pas déclencher trois emails d'affilée.
        if restants <= 0:
            if TYPE_ESSAI_TERMINE not in deja:
                if await _marquer_puis_envoyer(
                    db, user, TYPE_ESSAI_TERMINE,
                    lambda u=user, p=prenom: send_trial_ended(u.email, p),
                ):
                    bilan["essai_termine"] += 1
            continue

        # Le `continue` est inconditionnel : une fois dans la fenêtre de fin
        # d'essai, l'échéance prime. Sans cela, un artisan ayant déjà reçu son
        # avertissement retombait sur la relance d'activation et recevait un
        # « créez votre premier rapport » à trois jours de la coupure.
        if restants <= JOURS_AVANT_FIN:
            if TYPE_ESSAI_J3 not in deja:
                if await _marquer_puis_envoyer(
                    db, user, TYPE_ESSAI_J3,
                    lambda u=user, p=prenom, r=restants: send_trial_ending_soon(u.email, p, r),
                ):
                    bilan["essai_j3"] += 1
            continue

        if (
            anciennete >= JOURS_AVANT_RELANCE_ACTIVATION
            and TYPE_ACTIVATION not in deja
            and not await _a_cree_un_document(db, user.id)
        ):
            if await _marquer_puis_envoyer(
                db, user, TYPE_ACTIVATION,
                lambda u=user, p=prenom: send_activation_reminder(u.email, p),
            ):
                bilan["activation"] += 1

    logger.info(
        "Cycle de vie : %s compte(s) examiné(s) — %s activation, %s fin proche, %s terminé.",
        bilan["examines"], bilan["activation"], bilan["essai_j3"], bilan["essai_termine"],
    )
    return bilan


async def executer_tache_quotidienne() -> dict:
    """Point d'entrée de la tâche planifiée : ouvre sa propre session."""
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        try:
            return await traiter_cycle_vie(db)
        except Exception:
            logger.exception("La tâche de cycle de vie a échoué.")
            return {"examines": 0, "activation": 0, "essai_j3": 0, "essai_termine": 0, "erreur": True}
