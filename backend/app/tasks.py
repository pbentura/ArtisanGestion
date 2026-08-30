"""
Déclenchement manuel des tâches planifiées.

Utile pour tester, rattraper une exécution manquée, ou piloter les relances par
cron plutôt que par l'ordonnanceur interne (cas d'un déploiement multi-workers,
où l'ordonnanceur doit alors être désactivé avec SCHEDULER_ACTIF=false).

    docker compose exec backend python -m app.tasks relances
"""

import asyncio
import sys

# Charge tous les modèles : sans cela, les relations déclarées par nom
# ("Client", "Facture"…) ne se résolvent pas hors du contexte de app.main.
import app.models  # noqa: F401


def _relances() -> int:
    from app.services.relances import executer_tache_quotidienne

    bilan = asyncio.run(executer_tache_quotidienne())
    print(
        f"Relances — examinées : {bilan['examinees']}, "
        f"envoyées : {bilan['envoyees']}, ignorées : {bilan['ignorees']}"
    )
    return 1 if bilan.get("erreur") else 0


TACHES = {"relances": _relances}


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in TACHES:
        print(f"Usage : python -m app.tasks [{' | '.join(TACHES)}]", file=sys.stderr)
        return 2
    return TACHES[sys.argv[1]]()


if __name__ == "__main__":
    raise SystemExit(main())
