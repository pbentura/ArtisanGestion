from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class InvitationCreate(BaseModel):
    email: Optional[str] = None
    can_create_rapports: bool = True
    can_create_clients: bool = True
    can_create_devis: bool = False
    can_create_factures: bool = False
    can_invite: bool = False
    can_edit_societe: bool = False


class InvitationRead(BaseModel):
    id: int
    id_societe: int
    invited_by: int
    token: str
    email: Optional[str] = None
    can_create_rapports: bool
    can_create_clients: bool
    can_create_devis: bool
    can_create_factures: bool
    can_invite: bool
    can_edit_societe: bool
    status: str
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InvitationPublicRead(BaseModel):
    """Informations publiques visibles avant inscription (pas de token)."""
    id: int
    societe_nom: str
    invited_by_name: str
    email: Optional[str] = None
    can_create_rapports: bool
    can_create_clients: bool
    can_create_devis: bool
    can_create_factures: bool
    can_invite: bool
    can_edit_societe: bool
    status: str


class CollaborateurRead(BaseModel):
    id: int
    nom: str
    prenom: str
    email: str
    is_owner: bool
    can_create_rapports: bool
    can_create_clients: bool
    can_create_devis: bool
    can_create_factures: bool
    can_invite: bool
    can_edit_societe: bool

    class Config:
        from_attributes = True


class PermissionsUpdate(BaseModel):
    can_create_rapports: Optional[bool] = None
    can_create_clients: Optional[bool] = None
    can_create_devis: Optional[bool] = None
    can_create_factures: Optional[bool] = None
    can_invite: Optional[bool] = None
    can_edit_societe: Optional[bool] = None


class RegisterCollaborateurRequest(BaseModel):
    token: str
    nom: str
    prenom: str
    email: str
    mdp: str
