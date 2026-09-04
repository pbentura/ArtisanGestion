"""add stripe_customer_id to user

Mémorise le client Stripe rattaché à un compte. Jusqu'ici il était retrouvé
par email, or Stripe crée un nouveau client à chaque session de paiement :
avec deux clients pour la même adresse, le portail ouvrait le mauvais et un
abonnement devenait impossible à résilier par son titulaire.

Revision ID: e5b1d93c47a2
Revises: d4a8c2e51f37
Create Date: 2026-09-04 11:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e5b1d93c47a2'
down_revision: Union[str, None] = 'd4a8c2e51f37'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('stripe_customer_id', sa.String(length=255), nullable=True))
    op.create_index('ix_users_stripe_customer_id', 'users', ['stripe_customer_id'])


def downgrade() -> None:
    op.drop_index('ix_users_stripe_customer_id', table_name='users')
    op.drop_column('users', 'stripe_customer_id')
