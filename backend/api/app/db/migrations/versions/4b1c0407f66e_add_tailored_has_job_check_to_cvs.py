"""add tailored_has_job check to cvs

Revision ID: 4b1c0407f66e
Revises: 274f4771f7f3
Create Date: 2026-11-24 17:38:40.167695

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4b1c0407f66e"
down_revision: str | Sequence[str] | None = "274f4771f7f3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_check_constraint(
        "tailored_has_job", "cvs", "(kind = 'tailored') = (job_id IS NOT NULL)"
    )


def downgrade() -> None:
    op.drop_constraint("tailored_has_job", "cvs", type_="check")
