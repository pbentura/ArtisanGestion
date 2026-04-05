from pydantic import BaseModel
from typing import Optional

class ClientBase(BaseModel):
    nom: str
    adresse: Optional[str] = None
    code_postal: Optional[str] = None
    ville: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    siret: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(ClientBase):
    nom: Optional[str] = None

class Client(ClientBase):
    id: int
    id_user: int

    class Config:
        from_attributes = True
