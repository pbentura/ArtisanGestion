from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class SocieteBase(BaseModel):
    nom: str
    forme_juridique: Optional[str] = None
    logo: Optional[str] = None
    adresse: Optional[str] = None
    code_postal: Optional[str] = None
    ville: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    siret: Optional[str] = None
    iban: Optional[str] = None
    bic: Optional[str] = None
    nom_banque: Optional[str] = None
    capital_social: Optional[Decimal] = None
    rcs: Optional[str] = None
    tva_intracommunautaire: Optional[str] = None
    tva_defaut: Optional[Decimal] = None
    objectif_mensuel_ca: Optional[Decimal] = None
    texte_pied_page: Optional[str] = None
    couleur_document: Optional[str] = None

    # Relances impayés (automatisation réservée au plan Équipe)
    relances_actives: Optional[bool] = None
    relances_jours: Optional[str] = None

class SocieteCreate(SocieteBase):
    pass

class SocieteUpdate(BaseModel):
    nom: Optional[str] = None
    forme_juridique: Optional[str] = None
    logo: Optional[str] = None
    adresse: Optional[str] = None
    code_postal: Optional[str] = None
    ville: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    siret: Optional[str] = None
    iban: Optional[str] = None
    bic: Optional[str] = None
    nom_banque: Optional[str] = None
    capital_social: Optional[Decimal] = None
    rcs: Optional[str] = None
    tva_intracommunautaire: Optional[str] = None
    tva_defaut: Optional[Decimal] = None
    objectif_mensuel_ca: Optional[Decimal] = None
    texte_pied_page: Optional[str] = None
    couleur_document: Optional[str] = None

    # Relances impayés (automatisation réservée au plan Équipe)
    relances_actives: Optional[bool] = None
    relances_jours: Optional[str] = None

class SocieteRead(SocieteBase):
    id: int
    id_user: int
    stripe_connect_account_id: Optional[str] = None
    stripe_connect_enabled: bool = False
    stripe_connect_onboarding_complete: bool = False

    class Config:
        from_attributes = True
