"""added attendee table

Revision ID: 11e82daefb4a
Revises: 3bced71b80a2
Create Date: 2025-03-01 16:28:15.841796

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '11e82daefb4a'
down_revision: Union[str, None] = '3bced71b80a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('attendees',
    sa.Column('attendee_id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=255), nullable=False),
    sa.Column('last_name', sa.String(length=255), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('phone_number', sa.String(length=20), nullable=True),
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('check_in_status', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['events.event_id'], ),
    sa.PrimaryKeyConstraint('attendee_id')
    )
    op.create_index(op.f('ix_attendees_attendee_id'), 'attendees', ['attendee_id'], unique=False)
    op.create_index(op.f('ix_attendees_email'), 'attendees', ['email'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_attendees_email'), table_name='attendees')
    op.drop_index(op.f('ix_attendees_attendee_id'), table_name='attendees')
    op.drop_table('attendees')
    # ### end Alembic commands ###
