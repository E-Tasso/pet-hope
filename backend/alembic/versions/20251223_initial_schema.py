"""initial schema

Revision ID: 001
Revises:
Create Date: 2025-12-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types (IF NOT EXISTS for idempotency)
    op.execute("DO $$ BEGIN CREATE TYPE species AS ENUM ('dog', 'cat', 'bird', 'rodent', 'other'); EXCEPTION WHEN duplicate_object THEN null; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE size AS ENUM ('small', 'medium', 'large'); EXCEPTION WHEN duplicate_object THEN null; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE gender AS ENUM ('male', 'female', 'unknown'); EXCEPTION WHEN duplicate_object THEN null; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE animalstatus AS ENUM ('available', 'in_process', 'adopted'); EXCEPTION WHEN duplicate_object THEN null; END $$;")

    # Create animals table
    op.create_table(
        'animals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, index=True),
        sa.Column('species', postgresql.ENUM('dog', 'cat', 'bird', 'rodent', 'other', name='species', create_type=False), nullable=False, index=True),
        sa.Column('breed', sa.String(length=100), nullable=True),
        sa.Column('age_months', sa.Integer(), nullable=True),
        sa.Column('size', postgresql.ENUM('small', 'medium', 'large', name='size', create_type=False), nullable=False, index=True),
        sa.Column('gender', postgresql.ENUM('male', 'female', 'unknown', name='gender', create_type=False), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', postgresql.ENUM('available', 'in_process', 'adopted', name='animalstatus', create_type=False), nullable=False, index=True, server_default='available'),
        sa.Column('traits', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('special_needs', sa.Text(), nullable=True),
        sa.Column('location', sa.String(length=100), nullable=False, index=True),
        sa.Column('contact_info', postgresql.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # Create images table
    op.create_table(
        'images',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('animal_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('original_url', sa.String(length=500), nullable=False),
        sa.Column('thumbnail_url', sa.String(length=500), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false', index=True),
        sa.Column('order', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['animal_id'], ['animals.id'], ondelete='CASCADE'),
    )

    # Create indexes
    op.create_index('idx_animals_created_at', 'animals', ['created_at'])
    op.create_index('idx_images_animal_order', 'images', ['animal_id', 'order'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_images_animal_order', table_name='images')
    op.drop_index('idx_animals_created_at', table_name='animals')

    # Drop tables
    op.drop_table('images')
    op.drop_table('animals')

    # Drop enum types
    op.execute('DROP TYPE animalstatus')
    op.execute('DROP TYPE gender')
    op.execute('DROP TYPE size')
    op.execute('DROP TYPE species')
