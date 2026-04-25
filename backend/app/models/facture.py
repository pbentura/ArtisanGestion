from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, Date, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Facture(Base):
    __tablename__ = "factures"

    id = Column(Integer, primary_key=True, index=True)
    date_facture = Column(Date, nullable=False)
    numero_facture = Column(String, nullable=False, unique=True, index=True)
    titre_document_pdf = Column(String, nullable=False)
    objet_facture = Column(String, nullable=True)
    sous_total_ht = Column(Numeric(10, 2), nullable=False, server_default="0")
    total_tva = Column(Numeric(10, 2), nullable=False, server_default="0")
    total_ttc = Column(Numeric(10, 2), nullable=False, server_default="0")
    nb_jours_echeance = Column(Integer, nullable=False, server_default="30")
    date_echeance = Column(Date, nullable=True)
    statut = Column(String, nullable=False, server_default="brouillon")  # brouillon, validée
    est_payee = Column(Boolean, nullable=False, server_default="false")
    est_avoir = Column(Boolean, nullable=False, server_default="false")
    id_facture_source = Column(Integer, ForeignKey("factures.id"), nullable=True)
    conditions_particulieres = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    id_client = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="factures")

    id_user = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="factures")

    id_devis = Column(Integer, ForeignKey("devis.id", ondelete="SET NULL"), nullable=True)
    devis = relationship("Devis", back_populates="factures")

    lignes = relationship("LigneFacture", back_populates="facture", cascade="all, delete-orphan")
