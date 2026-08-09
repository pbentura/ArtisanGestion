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

    class Config:
        from_attributes = True


# Schema inline pour créer des lignes lors de la création d'un devis
from app.schemas.ligne_devis import LigneDevisCreate as LigneDevisCreateBase


class LigneDevisCreateInline(LigneDevisCreateBase):
    pass


DevisCreate.model_rebuild()
