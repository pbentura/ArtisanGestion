"""add emails cycle de vie

Trace des emails d'accompagnement de la période d'essai. La contrainte unique
(utilisateur, type) porte l'idempotence : c'est elle qui garantit qu'un artisan
ne reçoit jamais deux fois le même message, même si la tâche quotidienne est
rejouée.

Revision ID: d4a8c2e51f37
Revises: c3f7a1b90d24
Create Date: 2026-09-02 22:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4a8c2e51f37'
down_revision: Union[str, None] = 'c3f7a1b90d24'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'emails_cycle_vie',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('id_user', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column(
            'envoye_le',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['id_user'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id_user', 'type', name='uq_email_cycle_vie_user_type'),
    )
    op.create_index('ix_emails_cycle_vie_id', 'emails_cycle_vie', ['id'])
    op.create_index('ix_emails_cycle_vie_id_user', 'emails_cycle_vie', ['id_user'])


def downgrade() -> None:
    op.drop_index('ix_emails_cycle_vie_id_user', table_name='emails_cycle_vie')
    op.drop_index('ix_emails_cycle_vie_id', table_name='emails_cycle_vie')
    op.drop_table('emails_cycle_vie')
