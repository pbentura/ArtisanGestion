"""add acquisition attribution to user

Permet de relier un abonnement payant à la campagne qui a amené l'artisan.
Toutes les colonnes sont nullables : les comptes existants n'ont pas de
provenance connue, et un inscrit venu en direct n'en aura jamais.

Revision ID: c3f7a1b90d24
Revises: 21d35f015564
Create Date: 2026-09-02 21:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3f7a1b90d24'
down_revision: Union[str, None] = '21d35f015564'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


COLONNES = (
    'utm_source',
    'utm_medium',
    'utm_campaign',
    'utm_term',
    'utm_content',
    'gclid',
    'landing_page',
    'referrer',
)


def upgrade() -> None:
    for nom in COLONNES:
        op.add_column('users', sa.Column(nom, sa.String(length=255), nullable=True))

    # Les rapports d'acquisition filtrent systématiquement par campagne.
    op.create_index('ix_users_utm_campaign', 'users', ['utm_campaign'])


def downgrade() -> None:
    op.drop_index('ix_users_utm_campaign', table_name='users')
    for nom in reversed(COLONNES):
        op.drop_column('users', nom)
