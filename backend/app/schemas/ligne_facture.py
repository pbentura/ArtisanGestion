from pydantic import BaseModel, field_validator
from typing import Optional
from decimal import Decimal

TAUX_TVA_VALIDES = [Decimal("0"), Decimal("2.1"), Decimal("5.5"), Decimal("10"), Decimal("20")]


class LigneFactureBase(BaseModel):
    description: str
    quantite: Decimal
    prix_unite_ht: Decimal
    taux_tva: Decimal = Decimal("20")
    total_ht: Decimal

    @field_validator("taux_tva")
    @classmethod
    def valider_taux_tva(cls, v: Decimal) -> Decimal:
        if v not in TAUX_TVA_VALIDES:
            raise ValueError(f"Le taux de TVA doit être l'un des suivants : {', '.join(str(t) for t in TAUX_TVA_VALIDES)}%")
        return v


class LigneFactureCreate(LigneFactureBase):
    pass


class LigneFactureUpdate(BaseModel):
    description: Optional[str] = None
    quantite: Optional[Decimal] = None
    prix_unite_ht: Optional[Decimal] = None
    taux_tva: Optional[Decimal] = None
    total_ht: Optional[Decimal] = None

    @field_validator("taux_tva")
    @classmethod
    def valider_taux_tva(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v not in TAUX_TVA_VALIDES:
            raise ValueError(f"Le taux de TVA doit être l'un des suivants : {', '.join(str(t) for t in TAUX_TVA_VALIDES)}%")
        return v


class LigneFacture(LigneFactureBase):
    id: int
    id_facture: int

    class Config:
        from_attributes = True
