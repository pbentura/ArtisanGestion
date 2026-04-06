from pydantic import BaseModel, EmailStr
from typing import Optional, List
from .societe import SocieteRead

class UserBase(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    role: str = "USER"

class UserCreate(UserBase):
    mdp: str

class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserReadWithSocietes(UserRead):
    societes: List[SocieteRead] = []
