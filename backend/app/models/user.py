from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
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
    date_inscription = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Email verification
    is_email_verified = Column(Boolean, default=False, nullable=False, server_default="false")
    email_verification_token = Column(String, nullable=True)

    # Password reset
    password_reset_token = Column(String, nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)

    # Équipe / Collaborateurs
    id_societe = Column(Integer, ForeignKey("societe.id"), nullable=True)
    is_owner = Column(Boolean, default=True, nullable=False, server_default="true")

    # Permissions granulaires (pour les collaborateurs)
    can_create_rapports = Column(Boolean, default=True, nullable=False, server_default="true")
    can_create_clients = Column(Boolean, default=True, nullable=False, server_default="true")
    can_create_devis = Column(Boolean, default=True, nullable=False, server_default="true")
    can_create_factures = Column(Boolean, default=True, nullable=False, server_default="true")
    can_invite = Column(Boolean, default=False, nullable=False, server_default="false")
    can_edit_societe = Column(Boolean, default=False, nullable=False, server_default="false")

    # Relations existantes (propriétaire)
    societes = relationship("Societe", back_populates="user", cascade="all, delete-orphan", foreign_keys="Societe.id_user")
    clients = relationship("Client", back_populates="user", cascade="all, delete-orphan")
    rapports = relationship("Rapport", back_populates="user", cascade="all, delete-orphan")
    devis = relationship("Devis", back_populates="user", cascade="all, delete-orphan")
    factures = relationship("Facture", back_populates="user", cascade="all, delete-orphan")

    # Relation vers la société en tant que membre
    societe_membre = relationship("Societe", foreign_keys=[id_societe], backref="membres")

