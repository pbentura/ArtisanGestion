"""rename url_pdf to statut in rapports

Revision ID: 42f809c8c3ea
Revises: 32f809c8c3ea
Create Date: 2026-04-06 23:20:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision: str = '42f809c8c3ea'
down_revision: Union[str, None] = '32f809c8c3ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Rename column
    op.alter_column('rapports', 'url_pdf', new_column_name='statut')
    # Set default value and make it not nullable
    op.execute("UPDATE rapports SET statut = 'terminée' WHERE statut IS NULL")
    op.alter_column('rapports', 'statut', nullable=False, server_default='en cours')

def downgrade() -> None:
    op.alter_column('rapports', 'statut', new_column_name='url_pdf')
    op.alter_column('rapports', 'url_pdf', nullable=True, server_default=None)
