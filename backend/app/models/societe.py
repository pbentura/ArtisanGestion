from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Societe(Base):
    __tablename__ = "societe"

    id = Column(Integer, primary_key=True, index=True)
    logo = Column(String, nullable=True)
    nom = Column(String, index=True, nullable=False)
    adresse = Column(Text, nullable=True)
    code_postal = Column(String, nullable=True)
    ville = Column(String, nullable=True)
    telephone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    siret = Column(String, nullable=True)
    iban = Column(String, nullable=True)
    bic = Column(String, nullable=True)
    nom_banque = Column(String, nullable=True)
    capital_social = Column(Numeric(10, 2), nullable=True) # in €
    rcs = Column(String, nullable=True)
    tva_intracommunautaire = Column(String, nullable=True)
    forme_juridique = Column(String, nullable=True)
    tva_defaut = Column(Numeric(5, 2), nullable=True)
    dernier_numero_facture = Column(String, default="2024-001")
    objectif_mensuel_ca = Column(Numeric(15, 2), nullable=True) # in €
    texte_pied_page = Column(Text, nullable=True)

    id_user = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="societes", foreign_keys=[id_user])

    # Relations équipe
    invitations = relationship("Invitation", back_populates="societe", cascade="all, delete-orphan")

    # Relations données d'entreprise
    clients = relationship("Client", back_populates="societe", cascade="all, delete-orphan")
    devis = relationship("Devis", back_populates="societe", cascade="all, delete-orphan")
    factures = relationship("Facture", back_populates="societe", cascade="all, delete-orphan")
    rapports = relationship("Rapport", back_populates="societe", cascade="all, delete-orphan")
