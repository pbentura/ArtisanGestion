from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from app.schemas.client import Client as ClientSchema

class RapportBase(BaseModel):
    date_intervention: date
    titre_document_pdf: str
    id_client: Optional[int] = None
    contenu: Optional[str] = None
    photo_url: Optional[str] = None  # Legacy single photo
    photos: Optional[List[str]] = [] # Multiple photos
    statut: str = "en cours"
    id_devis: Optional[int] = None

class RapportCreate(RapportBase):
    pass

class RapportUpdate(RapportBase):
    date_intervention: Optional[date] = None
    titre_document_pdf: Optional[str] = None
    id_client: Optional[int] = None
    statut: Optional[str] = None
    photos: Optional[List[str]] = None
    id_devis: Optional[int] = None

class Rapport(RapportBase):
    id: int
    id_user: int
    created_at: datetime
    client: Optional[ClientSchema] = None
    devis: Optional[BaseModel] = None # Avoid circular import

    class Config:
        from_attributes = True
