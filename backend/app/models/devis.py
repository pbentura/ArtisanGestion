from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Devis(Base):
    __tablename__ = "devis"

    id = Column(Integer, primary_key=True, index=True)
    date_devis = Column(Date, nullable=False)
    numero_devis = Column(String, nullable=False, unique=True, index=True)
    titre_document_pdf = Column(String, nullable=False)
    objet_devis = Column(String, nullable=True)
    sous_total_ht = Column(Numeric(10, 2), nullable=False, server_default="0")
    total_tva = Column(Numeric(10, 2), nullable=False, server_default="0")
    total_ttc = Column(Numeric(10, 2), nullable=False, server_default="0")
    nb_jours_validite = Column(Integer, nullable=False, server_default="30")
    conditions_particulieres = Column(Text, nullable=True)
    statut = Column(String, nullable=False, server_default="brouillon")
    signature = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    id_client = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="devis")

    id_user = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="devis")

    id_rapport = Column(Integer, ForeignKey("rapports.id", ondelete="SET NULL"), nullable=True)
    rapport = relationship("Rapport", foreign_keys=[id_rapport])

    lignes = relationship("LigneDevis", back_populates="devis", cascade="all, delete-orphan")
    factures = relationship("Facture", back_populates="devis")
