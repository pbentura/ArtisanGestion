from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func

from app.core.database import Base


class EmailCycleVie(Base):
    """
    Trace d'un email d'accompagnement envoyé à un artisan pendant son essai.

    Même principe que les relances de factures : l'idempotence est portée par
    la base, pas par le calendrier. La contrainte d'unicité (utilisateur, type)
    garantit qu'un artisan ne reçoit jamais deux fois le même message, quel que
    soit le nombre d'exécutions de la tâche quotidienne — redémarrage du
    serveur, rattrapage après panne ou double processus.
    """

    __tablename__ = "emails_cycle_vie"
    __table_args__ = (
        UniqueConstraint("id_user", "type", name="uq_email_cycle_vie_user_type"),
    )

    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Voir app/services/cycle_vie.py pour les valeurs possibles.
    type = Column(String(50), nullable=False)
    envoye_le = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
