"""add_tva_intracommunautaire_to_clients

Revision ID: c84ef530479c
Revises: b73de430368b
Create Date: 2026-04-26 00:42:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c84ef530479c'
down_revision: Union[str, None] = 'b73de430368b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('clients', sa.Column('tva_intracommunautaire', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('clients', 'tva_intracommunautaire')
