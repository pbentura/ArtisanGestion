"""add couleur_document to societe

Revision ID: a7c9d2e4f801
Revises: f1a2b3c4d5e6
Create Date: 2026-08-17 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7c9d2e4f801'
down_revision: Union[str, None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('societe', sa.Column('couleur_document', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('societe', 'couleur_document')
