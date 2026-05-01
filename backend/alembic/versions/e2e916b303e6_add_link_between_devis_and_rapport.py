"""add_link_between_devis_and_rapport

Revision ID: e2e916b303e6
Revises: c84ef530479c
Create Date: 2026-05-01 19:15:32.884437

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2e916b303e6'
down_revision: Union[str, None] = 'c84ef530479c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add id_devis to rapports
    op.add_column('rapports', sa.Column('id_devis', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_rapports_devis', 'rapports', 'devis', ['id_devis'], ['id'], ondelete='SET NULL')
    
    # Add id_rapport to devis
    op.add_column('devis', sa.Column('id_rapport', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_devis_rapports', 'devis', 'rapports', ['id_rapport'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    # Remove id_rapport from devis
    op.drop_constraint('fk_devis_rapports', 'devis', type_='foreignkey')
    op.drop_column('devis', 'id_rapport')
    
    # Remove id_devis from rapports
    op.drop_constraint('fk_rapports_devis', 'rapports', type_='foreignkey')
    op.drop_column('rapports', 'id_devis')
