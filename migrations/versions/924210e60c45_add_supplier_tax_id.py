"""add supplier tax id

Revision ID: 924210e60c45
Revises: 12a3ec4e935e
Create Date: 2026-09-17 13:41:42.017796

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "924210e60c45"
down_revision: str | Sequence[str] | None = "12a3ec4e935e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "suppliers", sa.Column("tax_id", sa.String(length=50), nullable=False)
    )
    op.create_unique_constraint("uq_suppliers_tax_id", "suppliers", ["tax_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_suppliers_tax_id", "suppliers", type_="unique")
    op.drop_column("suppliers", "tax_id")
