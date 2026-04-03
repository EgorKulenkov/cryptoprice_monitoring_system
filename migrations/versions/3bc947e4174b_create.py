"""create

Revision ID: 3bc947e4174b
Revises: 
Create Date: 2026-04-03 02:16:54.891943

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3bc947e4174b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('createtime', sa.DateTime))



def downgrade() -> None:
    op.drop_column('users', 'createtime')
