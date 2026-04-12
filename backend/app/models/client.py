from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True, nullable=False)
    adresse = Column(Text, nullable=True)
    code_postal = Column(String, nullable=True)
    ville = Column(String, nullable=True)
    telephone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    siret = Column(String, nullable=True)
    
    id_user = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="clients")
    rapports = relationship("Rapport", back_populates="client", cascade="all, delete-orphan")
    devis = relationship("Devis", back_populates="client", cascade="all, delete-orphan")
