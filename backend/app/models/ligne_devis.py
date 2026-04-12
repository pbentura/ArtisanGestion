from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class LigneDevis(Base):
    __tablename__ = "lignes_devis"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    quantite = Column(Numeric(10, 2), nullable=False)
    prix_unite_ht = Column(Numeric(10, 2), nullable=False)
    taux_tva = Column(Numeric(4, 1), nullable=False, server_default="20.0")  # 0, 2.1, 5.5, 10, 20
    total_ht = Column(Numeric(10, 2), nullable=False)

    id_devis = Column(Integer, ForeignKey("devis.id", ondelete="CASCADE"), nullable=False)
    devis = relationship("Devis", back_populates="lignes")
