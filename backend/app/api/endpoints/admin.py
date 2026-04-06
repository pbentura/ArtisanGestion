"""
Admin API — Full database access for ADMIN users only.
All endpoints require a valid JWT token from a user with role == "ADMIN".
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import inspect as sa_inspect, text, delete

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.societe import Societe
from app.models.client import Client
from app.models.rapport import Rapport
from app.core.database import Base

router = APIRouter()

# ---------------------------------------------------------------------------
# Mapping table_name -> SQLAlchemy model
# ---------------------------------------------------------------------------
TABLE_MODELS = {
    "users": User,
    "societe": Societe,
    "clients": Client,
    "rapports": Rapport,
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
        # Convert non-JSON-serializable types to string
        if value is not None and not isinstance(value, (str, int, float, bool)):
            value = str(value)
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
            "default": str(col.default.arg) if col.default is not None and hasattr(col.default, "arg") else None,
        })
    return columns


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
    valid_keys = {col.key for col in mapper.columns}
    filtered = {k: v for k, v in data.items() if k in valid_keys and k != "id"}

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

    mapper = sa_inspect(model.__class__)
    valid_keys = {col.key for col in mapper.columns}

    for key, value in data.items():
        if key in valid_keys and key != "id":
            setattr(row, key, value)

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
