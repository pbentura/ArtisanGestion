from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from app.schemas.client import Client as ClientSchema
from app.schemas.ligne_devis import LigneDevis as LigneDevisSchema


class DevisBase(BaseModel):
    date_devis: date
    numero_devis: str
    titre_document_pdf: str
    id_client: int
    objet_devis: Optional[str] = None
    sous_total_ht: Decimal = Decimal("0")
    total_tva: Decimal = Decimal("0")
    total_ttc: Decimal = Decimal("0")
    nb_jours_validite: int = 30
    conditions_particulieres: Optional[str] = None
    statut: str = "brouillon"
    signature: Optional[str] = None


class DevisCreate(DevisBase):
    lignes: Optional[List["LigneDevisCreateInline"]] = []


class DevisUpdate(BaseModel):
    date_devis: Optional[date] = None
    numero_devis: Optional[str] = None
    titre_document_pdf: Optional[str] = None
    id_client: Optional[int] = None
    objet_devis: Optional[str] = None
    sous_total_ht: Optional[Decimal] = None
    total_tva: Optional[Decimal] = None
    total_ttc: Optional[Decimal] = None
    nb_jours_validite: Optional[int] = None
    conditions_particulieres: Optional[str] = None
    statut: Optional[str] = None
    signature: Optional[str] = None


class Devis(DevisBase):
    id: int
    id_user: int
    created_at: datetime
    client: Optional[ClientSchema] = None
    lignes: List[LigneDevisSchema] = []

    # Signature à distance : état visible par l'artisan.
    signature_nom: Optional[str] = None
    signature_le: Optional[datetime] = None
    signature_token_expire_le: Optional[datetime] = None
    est_en_attente_signature: bool = False

    class Config:
        from_attributes = True


# ── Signature électronique ──

class DemandeSignature(BaseModel):
    """Corps optionnel pour personnaliser l'envoi de la demande de signature."""
    email_client: Optional[str] = None


class LienSignature(BaseModel):
    url: str
    expire_le: datetime
    email_envoye_a: Optional[str] = None


class SocieteSignature(BaseModel):
    """Informations d'entreprise affichées sur la page publique de signature."""
    nom: str
    logo: Optional[str] = None
    adresse: Optional[str] = None
    code_postal: Optional[str] = None
    ville: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    siret: Optional[str] = None
    couleur_document: Optional[str] = None


class DevisPublic(BaseModel):
    """
    Vue restreinte d'un devis, exposée sans authentification à qui détient le
    lien de signature. N'expose ni identifiants internes, ni données d'autres
    documents.
    """
    numero_devis: str
    date_devis: date
    objet_devis: Optional[str] = None
    titre_document_pdf: str
    sous_total_ht: Decimal
    total_tva: Decimal
    total_ttc: Decimal
    nb_jours_validite: int
    conditions_particulieres: Optional[str] = None
    lignes: List[LigneDevisSchema] = []

    client_nom: str
    societe: SocieteSignature

    deja_signe: bool = False
    signature_nom: Optional[str] = None
    signature_le: Optional[datetime] = None


class SignatureSoumise(BaseModel):
    """Signature apposée par le client depuis la page publique."""
    signature: str          # data URL PNG du tracé
    nom_signataire: str
    email_signataire: Optional[str] = None
    accepte_conditions: bool = False


# Schema inline pour créer des lignes lors de la création d'un devis
from app.schemas.ligne_devis import LigneDevisCreate as LigneDevisCreateBase


class LigneDevisCreateInline(LigneDevisCreateBase):
    pass


DevisCreate.model_rebuild()
