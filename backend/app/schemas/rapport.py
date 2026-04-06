from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from app.schemas.client import Client as ClientSchema

class RapportBase(BaseModel):
    date_intervention: date
    titre_document_pdf: str
    id_client: int
    contenu: Optional[str] = None
    photo_url: Optional[str] = None
    statut: str = "en cours"

class RapportCreate(RapportBase):
    pass

class RapportUpdate(RapportBase):
    date_intervention: Optional[date] = None
    titre_document_pdf: Optional[str] = None
    id_client: Optional[int] = None
    statut: Optional[str] = None

class Rapport(RapportBase):
    id: int
    id_user: int
    created_at: datetime
    client: Optional[ClientSchema] = None

    class Config:
        from_attributes = True
