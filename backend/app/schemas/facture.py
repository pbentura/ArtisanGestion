from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from app.schemas.client import Client as ClientSchema
from app.schemas.ligne_facture import LigneFacture as LigneFactureSchema


class FactureBase(BaseModel):
    date_facture: date
    numero_facture: str
    titre_document_pdf: str
    id_client: int
    objet_facture: Optional[str] = None
    sous_total_ht: Decimal = Decimal("0")
    total_tva: Decimal = Decimal("0")
    total_ttc: Decimal = Decimal("0")
    nb_jours_echeance: int = 30
    date_echeance: Optional[date] = None
    conditions_particulieres: Optional[str] = None
    statut: str = "brouillon"
    est_payee: bool = False
    est_avoir: bool = False
    est_acompte: bool = False
    id_facture_source: Optional[int] = None


class FactureCreate(FactureBase):
    id_devis: Optional[int] = None
    lignes: Optional[List["LigneFactureCreateInline"]] = []


class FactureCreateFromDevis(BaseModel):
    """Schéma minimaliste pour créer une facture depuis un devis existant."""
    date_facture: Optional[date] = None
    numero_facture: Optional[str] = None
    titre_document_pdf: str = "FACTURE"
    nb_jours_echeance: int = 30
    conditions_particulieres: Optional[str] = None
    statut: str = "brouillon"


class FactureUpdate(BaseModel):
    date_facture: Optional[date] = None
    numero_facture: Optional[str] = None
    titre_document_pdf: Optional[str] = None
    id_client: Optional[int] = None
    objet_facture: Optional[str] = None
    sous_total_ht: Optional[Decimal] = None
    total_tva: Optional[Decimal] = None
    total_ttc: Optional[Decimal] = None
    nb_jours_echeance: Optional[int] = None
    date_echeance: Optional[date] = None
    conditions_particulieres: Optional[str] = None
    statut: Optional[str] = None
    est_payee: Optional[bool] = None
    est_avoir: Optional[bool] = None
    est_acompte: Optional[bool] = None
    id_facture_source: Optional[int] = None


class Facture(FactureBase):
    id: int
    id_user: int
    id_devis: Optional[int] = None
    created_at: datetime
    client: Optional[ClientSchema] = None
    lignes: List[LigneFactureSchema] = []

    class Config:
        from_attributes = True


# Schema inline pour créer des lignes lors de la création d'une facture
from app.schemas.ligne_facture import LigneFactureCreate as LigneFactureCreateBase


class LigneFactureCreateInline(LigneFactureCreateBase):
    pass


FactureCreate.model_rebuild()
