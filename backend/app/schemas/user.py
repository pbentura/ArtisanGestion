from pydantic import BaseModel, EmailStr, computed_field
from typing import Optional, List
from datetime import datetime, timezone
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
    has_password: bool = False
    onboarding_draft: Optional[dict] = None
    date_inscription: Optional[datetime] = None
    
    # Équipe
    id_societe: Optional[int] = None
    active_societe_id: Optional[int] = None
    is_owner: bool = True
    
    # Permissions
    can_create_rapports: bool = True
    can_create_clients: bool = True
    can_create_devis: bool = True
    can_create_factures: bool = True
    can_invite: bool = False
    can_edit_societe: bool = False

    @computed_field
    @property
    def trial_days_remaining(self) -> int:
        if self.role == "ADMIN":
            return 9999
        if not self.date_inscription:
            return 0
        now = datetime.now(timezone.utc)
        delta = now - self.date_inscription
        remaining = 14 - delta.days
        return max(0, remaining)

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[EmailStr] = None
    onboarding_draft: Optional[dict] = None

class UserPasswordUpdate(BaseModel):
    current_password: Optional[str] = None
    new_password: str

class UserReadWithSocietes(UserRead):
    societes: List[SocieteRead] = []

class UserRegisterResponse(BaseModel):
    user: UserRead
    waiting_token: str
