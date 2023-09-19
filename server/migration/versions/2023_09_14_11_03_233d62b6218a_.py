"""empty message

Revision ID: 233d62b6218a
Revises: c42371aa8c16
Create Date: 2023-09-14 11:03:58.736928

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '233d62b6218a'
down_revision: Union[str, None] = 'c42371aa8c16'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('exchange_rates__fiat_currency', sa.Column('exchange_rate_id', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('exchange_rates__fiat_currency', 'exchange_rate_id')
    # ### end Alembic commands ###
