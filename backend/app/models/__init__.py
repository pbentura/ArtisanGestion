"""
Point d'import unique des modèles.

Les relations SQLAlchemy sont déclarées par nom de classe ("Client", "Facture"…) :
elles ne se résolvent que si tous les modèles ont été importés au préalable.
Importer ce paquet garantit une registry complète — indispensable pour les
points d'entrée qui ne passent pas par `app.main`, comme la tâche cron
`python -m app.tasks` ou un script ponctuel.
"""

from app.models.user import User
from app.models.societe import Societe
from app.models.client import Client
from app.models.rapport import Rapport
from app.models.devis import Devis
from app.models.ligne_devis import LigneDevis
from app.models.facture import Facture
from app.models.ligne_facture import LigneFacture
from app.models.invitation import Invitation
from app.models.relance import RelanceFacture

__all__ = [
    "User",
    "Societe",
    "Client",
    "Rapport",
    "Devis",
    "LigneDevis",
    "Facture",
    "LigneFacture",
    "Invitation",
    "RelanceFacture",
]
