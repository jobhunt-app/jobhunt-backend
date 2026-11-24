"""enable pgvector extension

Revision ID: 6487d6790df0
Revises: a7d806236896
Create Date: 2026-11-24 17:53:36.525857

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6487d6790df0"
down_revision: str | Sequence[str] | None = "a7d806236896"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Needed for vector(1536) embedding columns (M5). Autogenerate can't detect extensions.
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP EXTENSION IF EXISTS vector")
