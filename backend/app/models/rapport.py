from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base

class Rapport(Base):
    __tablename__ = "rapports"

    id = Column(Integer, primary_key=True, index=True)
    date_intervention = Column(Date, nullable=False)
    titre_document_pdf = Column(String, nullable=False)
    contenu = Column(Text, nullable=True)
    photo_url = Column(String, nullable=True)  # Legacy single photo
    photos = Column(JSONB, nullable=True, server_default='[]') # Multiple photos
    statut = Column(String, nullable=False, server_default="en cours")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    id_client = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="rapports")
    
    id_user = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="rapports")

    id_devis = Column(Integer, ForeignKey("devis.id", ondelete="SET NULL"), nullable=True)
    devis = relationship("Devis", back_populates="rapport", foreign_keys=[id_devis])
