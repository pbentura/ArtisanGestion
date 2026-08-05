from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    prenom = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    mdp = Column(String, nullable=True)
    role = Column(String, default="USER", nullable=True)
    onboarding_draft = Column(JSON, nullable=True)

    # Email verification
    is_email_verified = Column(Boolean, default=False, nullable=False, server_default="false")
    email_verification_token = Column(String, nullable=True)

    # Password reset
    password_reset_token = Column(String, nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)

    societes = relationship("Societe", back_populates="user", cascade="all, delete-orphan")
    clients = relationship("Client", back_populates="user", cascade="all, delete-orphan")
    rapports = relationship("Rapport", back_populates="user", cascade="all, delete-orphan")
    devis = relationship("Devis", back_populates="user", cascade="all, delete-orphan")
    factures = relationship("Facture", back_populates="user", cascade="all, delete-orphan")
