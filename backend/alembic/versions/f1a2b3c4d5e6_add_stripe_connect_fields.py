"""add stripe connect fields

Revision ID: f1a2b3c4d5e6
Revises: e1facc9ad420
Create Date: 2026-08-11 05:31:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, None] = 'e1facc9ad420'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Societe — Stripe Connect columns
    op.add_column('societe', sa.Column('stripe_connect_account_id', sa.String(), nullable=True))
    op.add_column('societe', sa.Column('stripe_connect_enabled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('societe', sa.Column('stripe_connect_onboarding_complete', sa.Boolean(), nullable=False, server_default='false'))

    # Factures — Stripe payment columns
    op.add_column('factures', sa.Column('stripe_checkout_session_id', sa.String(), nullable=True))
    op.add_column('factures', sa.Column('stripe_payment_url', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('factures', 'stripe_payment_url')
    op.drop_column('factures', 'stripe_checkout_session_id')
    op.drop_column('societe', 'stripe_connect_onboarding_complete')
    op.drop_column('societe', 'stripe_connect_enabled')
    op.drop_column('societe', 'stripe_connect_account_id')
