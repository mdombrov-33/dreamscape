"""add pgvector and embedding column

Revision ID: 4c500d3a38da
Revises: 43bd000b6db1
Create Date: 2026-02-19 14:51:54.929123

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c500d3a38da'
down_revision: Union[str, Sequence[str], None] = '43bd000b6db1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Add embedding column (384 dimensions for all-MiniLM-L6-v2)
    op.execute("ALTER TABLE dreams ADD COLUMN embedding vector(384)")

    # Create index for similarity search (cosine distance)
    op.execute("CREATE INDEX dreams_embedding_idx ON dreams USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS dreams_embedding_idx")
    op.execute("ALTER TABLE dreams DROP COLUMN IF EXISTS embedding")
    op.execute("DROP EXTENSION IF EXISTS vector")
