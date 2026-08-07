from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, index=True)
    id_societe = Column(Integer, ForeignKey("societe.id"), nullable=False)
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, nullable=True)  # Optionnel : pré-remplir l'email

    # Permissions pré-définies pour le futur collaborateur
    can_create_rapports = Column(Boolean, default=True, nullable=False)
    can_create_clients = Column(Boolean, default=True, nullable=False)
    can_create_devis = Column(Boolean, default=False, nullable=False)
    can_create_factures = Column(Boolean, default=False, nullable=False)
    can_invite = Column(Boolean, default=False, nullable=False)
    can_edit_societe = Column(Boolean, default=False, nullable=False)

    status = Column(String, default="pending", nullable=False)  # pending, accepted, expired
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)  # 7 jours par défaut

    # Relations
    societe = relationship("Societe", back_populates="invitations")
    inviter = relationship("User", foreign_keys=[invited_by])
