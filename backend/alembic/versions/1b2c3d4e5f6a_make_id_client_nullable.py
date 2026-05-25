"""make_id_client_nullable

Revision ID: 1b2c3d4e5f6a
Revises: e2e916b303e6
Create Date: 2026-05-25 22:54:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1b2c3d4e5f6a'
down_revision: Union[str, None] = 'e2e916b303e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('rapports', 'id_client',
               existing_type=sa.INTEGER(),
               nullable=True)


def downgrade() -> None:
    op.alter_column('rapports', 'id_client',
               existing_type=sa.INTEGER(),
               nullable=False)
