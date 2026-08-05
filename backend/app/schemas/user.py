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
    onboarding_draft: Optional[dict] = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[EmailStr] = None
    onboarding_draft: Optional[dict] = None

class UserReadWithSocietes(UserRead):
    societes: List[SocieteRead] = []
