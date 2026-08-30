from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class RelanceFacture(Base):
    """
    Trace d'une relance envoyée pour une facture impayée.

    Sert deux rôles : garder l'historique visible par l'artisan, et garantir
    l'idempotence — la contrainte d'unicité (facture, niveau) empêche qu'un
    même palier de relance parte deux fois, même si la tâche planifiée est
    rejouée ou exécutée par deux processus.
    """

    __tablename__ = "relances_facture"
    __table_args__ = (
        UniqueConstraint("id_facture", "niveau", name="uq_relance_facture_niveau"),
    )

    id = Column(Integer, primary_key=True, index=True)
    id_facture = Column(
        Integer, ForeignKey("factures.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # 1 pour la première relance, 2 pour la deuxième, etc.
    niveau = Column(Integer, nullable=False)
    jours_de_retard = Column(Integer, nullable=False, server_default="0")

    destinataire = Column(String, nullable=False)
    envoyee_le = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # False lorsque l'artisan a déclenché la relance à la main.
    automatique = Column(Boolean, nullable=False, server_default="true")

    facture = relationship("Facture", back_populates="relances")
