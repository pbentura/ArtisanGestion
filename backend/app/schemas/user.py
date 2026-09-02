from pydantic import BaseModel, EmailStr, model_validator
from typing import Optional, List
from datetime import datetime, timezone
from .societe import SocieteRead

# Un abonnement actif n'a pas de compte à rebours : cette valeur signale
# « pas de limite » au frontend, qui teste `trial_days_remaining === 0`.
ESSAI_ILLIMITE = 9999

DUREE_ESSAI_JOURS = 14


def jours_essai_restants(role: Optional[str], date_inscription: Optional[datetime]) -> int:
    """
    Jours d'essai restants pour un compte isolé.

    PREMIUM et TEAM sont des abonnements actifs : les omettre ici faisait
    afficher « essai terminé » à des clients qui payent, et le frontend leur
    proposait de se réabonner au lieu de les laisser travailler.
    """
    if role in ("ADMIN", "PREMIUM", "TEAM"):
        return ESSAI_ILLIMITE
    if not date_inscription:
        return 0
    inscription = date_inscription
    if inscription.tzinfo is None:
        inscription = inscription.replace(tzinfo=timezone.utc)
    ecoules = (datetime.now(timezone.utc) - inscription).days
    return max(0, DUREE_ESSAI_JOURS - ecoules)


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

    # Jours d'essai restants.
    #
    # Renseigné par l'API, car le calcul exact demande la base : un
    # collaborateur profite de l'abonnement de son patron, et son propre
    # compte n'en dit rien. La valeur de repli calculée ci-dessous couvre le
    # cas d'un compte isolé.
    trial_days_remaining: Optional[int] = None

    @model_validator(mode="after")
    def _valeur_essai_par_defaut(self):
        if self.trial_days_remaining is None:
            self.trial_days_remaining = jours_essai_restants(
                self.role, self.date_inscription
            )
        return self

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
