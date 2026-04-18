from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class LigneFacture(Base):
    __tablename__ = "lignes_facture"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    quantite = Column(Numeric(10, 2), nullable=False)
    prix_unite_ht = Column(Numeric(10, 2), nullable=False)
    taux_tva = Column(Numeric(4, 1), nullable=False, server_default="20.0")  # 0, 2.1, 5.5, 10, 20
    total_ht = Column(Numeric(10, 2), nullable=False)

    id_facture = Column(Integer, ForeignKey("factures.id", ondelete="CASCADE"), nullable=False)
    facture = relationship("Facture", back_populates="lignes")
