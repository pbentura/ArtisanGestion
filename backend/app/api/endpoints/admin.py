"""
Admin API — Full database access for ADMIN users only.
All endpoints require a valid JWT token from a user with role == "ADMIN".
"""

from typing import Any, Dict, List
import datetime
from decimal import Decimal, InvalidOperation
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import inspect as sa_inspect, text, delete

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.societe import Societe
from app.models.client import Client
from app.models.rapport import Rapport
from app.models.devis import Devis
from app.models.ligne_devis import LigneDevis
from app.core.database import Base

router = APIRouter()

# Contexte bcrypt — utilisé pour hasher le mdp si un user est créé via l'admin
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Colonnes qui ne doivent jamais être écrites directement depuis le payload
READONLY_COLS = {"id", "created_at"}

# ---------------------------------------------------------------------------
# Mapping table_name -> SQLAlchemy model
# ---------------------------------------------------------------------------
TABLE_MODELS = {
    "users": User,
    "societe": Societe,
    "clients": Client,
    "rapports": Rapport,
    "devis": Devis,
    "lignes_devis": LigneDevis,
}


def _get_model(table_name: str):
    model = TABLE_MODELS.get(table_name)
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table '{table_name}' introuvable",
        )
    return model


# ---------------------------------------------------------------------------
# Dependency: ensure current user is ADMIN
# ---------------------------------------------------------------------------
async def get_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé — rôle ADMIN requis",
        )
    return current_user


# ---------------------------------------------------------------------------
# Helper: serialize a row to dict using column inspection
# ---------------------------------------------------------------------------
def _row_to_dict(row) -> Dict[str, Any]:
    mapper = sa_inspect(row.__class__)
    result = {}
    for col in mapper.columns:
        value = getattr(row, col.key)
        if value is None:
            result[col.key] = None
        elif isinstance(value, (datetime.date, datetime.datetime)):
            result[col.key] = value.isoformat()
        elif isinstance(value, Decimal):
            result[col.key] = float(value)
        elif not isinstance(value, (str, int, float, bool)):
            result[col.key] = str(value)
        else:
            result[col.key] = value
    return result


# ---------------------------------------------------------------------------
# Helper: get column schema info for a model
# ---------------------------------------------------------------------------
def _get_table_schema(model) -> List[Dict[str, Any]]:
    mapper = sa_inspect(model)
    columns = []
    for col in mapper.columns:
        col_type = str(col.type)
        columns.append({
            "name": col.key,
            "type": col_type,
            "nullable": col.nullable if hasattr(col, "nullable") else True,
            "primary_key": col.primary_key if hasattr(col, "primary_key") else False,
            "default": (
                str(col.default.arg)
                if col.default is not None
                and hasattr(col.default, "arg")
                and not callable(col.default.arg)
                else None
            ),
        })
    return columns


# ---------------------------------------------------------------------------
# Helper: coerce a raw JSON value to the Python type expected by SQLAlchemy
# ---------------------------------------------------------------------------
def _coerce_value(col, value: Any) -> Any:
    """Convert a string value to the appropriate Python type based on the SA column type."""
    if value is None:
        return None
    col_type = type(col.type).__name__.upper()
    try:
        if col_type == "DATE":
            if isinstance(value, str):
                return datetime.date.fromisoformat(value[:10])  # coupe le T+heure si present
        elif col_type in ("DATETIME", "TIMESTAMP"):
            if isinstance(value, str):
                return datetime.datetime.fromisoformat(value)
        elif col_type in ("NUMERIC", "FLOAT", "REAL", "DOUBLE_PRECISION"):
            if isinstance(value, str):
                return Decimal(value)
            if isinstance(value, float):
                return Decimal(str(value))
        elif col_type in ("INTEGER", "BIGINTEGER", "SMALLINTEGER"):
            if isinstance(value, (str, float)):
                return int(value)
        elif col_type == "BOOLEAN":
            if isinstance(value, str):
                return value.lower() in ("true", "1", "yes")
    except (ValueError, InvalidOperation):
        pass
    return value


# ===========================================================================
# Endpoints
# ===========================================================================

@router.get("/tables", response_model=List[str])
async def list_tables(
    admin: User = Depends(get_admin_user),
):
    """Liste des tables disponibles."""
    return list(TABLE_MODELS.keys())


@router.get("/tables/{table_name}/schema")
async def get_table_schema(
    table_name: str,
    admin: User = Depends(get_admin_user),
):
    """Retourne le schéma (colonnes) d'une table."""
    model = _get_model(table_name)
    return _get_table_schema(model)


@router.get("/tables/{table_name}")
async def get_table_rows(
    table_name: str,
    skip: int = 0,
    limit: int = 500,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Retourne toutes les lignes d'une table."""
    model = _get_model(table_name)
    result = await db.execute(select(model).offset(skip).limit(limit))
    rows = result.scalars().all()
    return [_row_to_dict(r) for r in rows]


@router.post("/tables/{table_name}", status_code=status.HTTP_201_CREATED)
async def create_row(
    table_name: str,
    data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Crée une nouvelle ligne dans la table."""
    model = _get_model(table_name)

    # Filter out keys that are not valid columns
    mapper = sa_inspect(model)
    col_map = {col.key: col for col in mapper.columns}
    filtered = {
        k: _coerce_value(col_map[k], v)
        for k, v in data.items()
        if k in col_map and k not in READONLY_COLS
    }

    # Hash le mot de passe si on crée un user
    if table_name == "users" and "mdp" in filtered and filtered["mdp"]:
        filtered["mdp"] = _pwd_context.hash(filtered["mdp"][:72])

    row = model(**filtered)
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return _row_to_dict(row)


@router.put("/tables/{table_name}/{row_id}")
async def update_row(
    table_name: str,
    row_id: int,
    data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Met à jour une ligne existante."""
    model = _get_model(table_name)
    result = await db.execute(select(model).where(model.id == row_id))
    row = result.scalars().first()

    if not row:
        raise HTTPException(status_code=404, detail="Ligne introuvable")

    mapper = sa_inspect(model)
    col_map = {col.key: col for col in mapper.columns}

    for key, value in data.items():
        if key in col_map and key not in READONLY_COLS:
            setattr(row, key, _coerce_value(col_map[key], value))

    # Hash le mot de passe si on met à jour un user
    if table_name == "users" and "mdp" in data and data["mdp"]:
        row.mdp = _pwd_context.hash(data["mdp"][:72])

    await db.commit()
    await db.refresh(row)
    return _row_to_dict(row)


@router.delete("/tables/{table_name}/{row_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_row(
    table_name: str,
    row_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Supprime une ligne."""
    model = _get_model(table_name)
    result = await db.execute(select(model).where(model.id == row_id))
    row = result.scalars().first()

    if not row:
        raise HTTPException(status_code=404, detail="Ligne introuvable")

    await db.delete(row)
    await db.commit()
    return None
