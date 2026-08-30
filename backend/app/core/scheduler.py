"""
Tâches planifiées.

L'ordonnanceur vit dans le processus applicatif : c'est suffisant tant que
l'API tourne en un seul worker, ce qui est le cas aujourd'hui. Si vous passez
à plusieurs workers ou plusieurs conteneurs, chacun démarrerait sa propre
instance — mettez alors RELANCES_ACTIVES=false partout sauf sur un processus
dédié, ou déclenchez la tâche par cron via `python -m app.tasks`.

L'envoi reste protégé par l'unicité (facture, niveau) en base : même exécutée
plusieurs fois, la tâche n'enverra pas deux fois la même relance.
"""

import logging
import os
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

_scheduler: Optional[AsyncIOScheduler] = None


def _actif() -> bool:
    """Les tâches planifiées sont désactivables sans toucher au code."""
    return os.getenv("SCHEDULER_ACTIF", "true").strip().lower() not in ("false", "0", "no")


def demarrer() -> Optional[AsyncIOScheduler]:
    """Démarre l'ordonnanceur et enregistre les tâches récurrentes."""
    global _scheduler

    if not _actif():
        logger.info("Ordonnanceur désactivé (SCHEDULER_ACTIF=false).")
        return None

    if _scheduler and _scheduler.running:
        return _scheduler

    from app.services.relances import executer_tache_quotidienne

    heure = int(os.getenv("RELANCES_HEURE", "9"))
    fuseau = os.getenv("SCHEDULER_TIMEZONE", "Europe/Paris")

    _scheduler = AsyncIOScheduler(timezone=fuseau)
    _scheduler.add_job(
        executer_tache_quotidienne,
        trigger=CronTrigger(hour=heure, minute=0),
        id="relances_impayes",
        name="Relances des factures impayées",
        # Si le serveur était arrêté à l'heure prévue, on rattrape dans l'heure
        # qui suit plutôt que de sauter la journée.
        misfire_grace_time=3600,
        # Jamais deux exécutions simultanées de la même tâche.
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    _scheduler.start()
    logger.info(
        "Ordonnanceur démarré — relances quotidiennes à %sh00 (%s).", heure, fuseau
    )
    return _scheduler


def arreter() -> None:
    """Arrêt propre, sans attendre les tâches en cours."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Ordonnanceur arrêté.")
    _scheduler = None
