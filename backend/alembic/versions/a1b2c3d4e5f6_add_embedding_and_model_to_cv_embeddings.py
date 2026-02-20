"""add_embedding_and_model_to_cv_embeddings

Revision ID: a1b2c3d4e5f6
Revises: 47e16915b715
Create Date: 2026-02-20 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '47e16915b715'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing embedding (vector) and model columns to cv_embeddings.
    
    These columns were defined in the SQLAlchemy model but missing from
    the initial migration. The embedding column uses pgvector's Vector
    type for 1536-dimensional OpenAI embeddings.
    """
    # Ensure pgvector extension exists (idempotent)
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Add the vector embedding column
    op.add_column('cv_embeddings', sa.Column('embedding', Vector(1536), nullable=True))
    
    # Add the model name column
    op.add_column('cv_embeddings', sa.Column('model', sa.String(100), nullable=True))


def downgrade() -> None:
    """Remove embedding and model columns."""
    op.drop_column('cv_embeddings', 'model')
    op.drop_column('cv_embeddings', 'embedding')
