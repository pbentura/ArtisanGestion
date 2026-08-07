"""add team system (invitations, user permissions, id_societe)

Revision ID: a8b9c0d1e2f3
Revises: 1f7d9ed83f48
Create Date: 2026-08-07 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8b9c0d1e2f3'
down_revision: Union[str, None] = '1f7d9ed83f48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Créer la table invitations
    op.create_table(
        'invitations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('id_societe', sa.Integer(), sa.ForeignKey('societe.id'), nullable=False),
        sa.Column('invited_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('token', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('can_create_rapports', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('can_create_clients', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('can_create_devis', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('can_create_factures', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('can_invite', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('can_edit_societe', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    )

    # 2. Ajouter les colonnes équipe/permissions à la table users
    op.add_column('users', sa.Column('id_societe', sa.Integer(), sa.ForeignKey('societe.id'), nullable=True))
    op.add_column('users', sa.Column('is_owner', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('can_create_rapports', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('can_create_clients', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('can_create_devis', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('can_create_factures', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('can_invite', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('can_edit_societe', sa.Boolean(), nullable=False, server_default='false'))

    # 3. Migrer les données : remplir id_societe pour les utilisateurs existants
    # Chaque propriétaire existant reçoit l'id de sa première société
    op.execute("""
        UPDATE users
        SET id_societe = (
            SELECT societe.id FROM societe WHERE societe.id_user = users.id LIMIT 1
        )
        WHERE EXISTS (
            SELECT 1 FROM societe WHERE societe.id_user = users.id
        )
    """)


def downgrade() -> None:
    op.drop_column('users', 'can_edit_societe')
    op.drop_column('users', 'can_invite')
    op.drop_column('users', 'can_create_factures')
    op.drop_column('users', 'can_create_devis')
    op.drop_column('users', 'can_create_clients')
    op.drop_column('users', 'can_create_rapports')
    op.drop_column('users', 'is_owner')
    op.drop_column('users', 'id_societe')
    op.drop_table('invitations')
