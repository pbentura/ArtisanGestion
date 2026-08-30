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

    # ── Signature électronique ──
    # `signature` contient l'image tracée (data URL PNG), qu'elle ait été
    # apposée sur place ou à distance.
    signature = Column(Text, nullable=True)

    # Signature à distance : jeton du lien public envoyé au client.
    signature_token = Column(String, nullable=True, unique=True, index=True)
    signature_token_expire_le = Column(DateTime(timezone=True), nullable=True)

    # Preuve de signature (valeur probante d'une signature simple eIDAS) :
    # qui a signé, quand, depuis où, et sur quelle version du document.
    signature_nom = Column(String, nullable=True)
    signature_email = Column(String, nullable=True)
    signature_le = Column(DateTime(timezone=True), nullable=True)
    signature_ip = Column(String, nullable=True)
    signature_user_agent = Column(Text, nullable=True)
    # Empreinte SHA-256 du contenu au moment de la signature : permet de
    # démontrer qu'il n'a pas été modifié après coup.
    signature_empreinte = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    id_client = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="devis")

    id_user = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="devis")
    
    id_societe = Column(Integer, ForeignKey("societe.id"), nullable=True)
    societe = relationship("Societe", back_populates="devis")

    lignes = relationship("LigneDevis", back_populates="devis", cascade="all, delete-orphan")
    factures = relationship("Facture", back_populates="devis")

    @property
    def est_en_attente_signature(self) -> bool:
        """Un lien de signature a été envoyé, le client n'a pas encore signé."""
        return bool(self.signature_token and not self.signature_le)
