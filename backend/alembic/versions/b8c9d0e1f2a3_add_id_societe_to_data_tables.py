"""add id_societe to data tables

Revision ID: b8c9d0e1f2a3
Revises: a8b9c0d1e2f3
Create Date: 2026-08-07 12:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8c9d0e1f2a3'
down_revision: Union[str, None] = 'a8b9c0d1e2f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Ajouter les colonnes id_societe
    op.add_column('clients', sa.Column('id_societe', sa.Integer(), sa.ForeignKey('societe.id'), nullable=True))
    op.add_column('devis', sa.Column('id_societe', sa.Integer(), sa.ForeignKey('societe.id'), nullable=True))
    op.add_column('factures', sa.Column('id_societe', sa.Integer(), sa.ForeignKey('societe.id'), nullable=True))
    op.add_column('rapports', sa.Column('id_societe', sa.Integer(), sa.ForeignKey('societe.id'), nullable=True))

    # 2. Remplir id_societe en utilisant l'id_societe de l'utilisateur qui a créé la ressource
    # (Ou en utilisant la table societe si l'utilisateur est le propriétaire)
    op.execute("""
        UPDATE clients SET id_societe = (
            SELECT id_societe FROM users WHERE users.id = clients.id_user LIMIT 1
        )
    """)
    op.execute("""
        UPDATE devis SET id_societe = (
            SELECT id_societe FROM users WHERE users.id = devis.id_user LIMIT 1
        )
    """)
    op.execute("""
        UPDATE factures SET id_societe = (
            SELECT id_societe FROM users WHERE users.id = factures.id_user LIMIT 1
        )
    """)
    op.execute("""
        UPDATE rapports SET id_societe = (
            SELECT id_societe FROM users WHERE users.id = rapports.id_user LIMIT 1
        )
    """)


def downgrade() -> None:
    op.drop_column('rapports', 'id_societe')
    op.drop_column('factures', 'id_societe')
    op.drop_column('devis', 'id_societe')
    op.drop_column('clients', 'id_societe')
