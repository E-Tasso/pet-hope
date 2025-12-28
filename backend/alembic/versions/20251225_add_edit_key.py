"""add edit key hash field

Revision ID: 002
Revises: 001
Create Date: 2025-12-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Pre-calculated bcrypt hash for "pethope123" (default edit key for testing)
# Generated with: bcrypt.hashpw(b'pethope123', bcrypt.gensalt())
DEFAULT_HASH = "$2b$12$ieDD/RKyg.DZTZV39NdwGeywvYiasF7yECfS/CzScUhLeFVu1h2sS"


def upgrade() -> None:
    # Add edit_key_hash column
    op.add_column(
        'animals',
        sa.Column('edit_key_hash', sa.String(length=255), nullable=True)
    )

    # Set default hash for existing animals (password: pethope123)
    op.execute(
        f"UPDATE animals SET edit_key_hash = '{DEFAULT_HASH}' WHERE edit_key_hash IS NULL"
    )


def downgrade() -> None:
    op.drop_column('animals', 'edit_key_hash')
