"""empty message

Revision ID: 1b67627da56e
Revises: 
Create Date: 2024-12-11 15:35:12.349225

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1b67627da56e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('photo', sa.String(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('age', sa.Integer(), nullable=False),
    sa.Column('gender', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('filter_by_age', sa.String(), nullable=True),
    sa.Column('filter_by_gender', sa.String(), nullable=False),
    sa.Column('filter_by_description', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user')),
    schema='public'
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user', schema='public')
    # ### end Alembic commands ###
