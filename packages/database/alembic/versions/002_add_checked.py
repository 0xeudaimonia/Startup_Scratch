"""Add is_checked flags to companies and jobs."""

from alembic import op
import sqlalchemy as sa

revision = "002_add_checked"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "companies",
        sa.Column("is_checked", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "jobs",
        sa.Column("is_checked", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_companies_is_checked", "companies", ["is_checked"])
    op.create_index("ix_jobs_is_checked", "jobs", ["is_checked"])


def downgrade() -> None:
    op.drop_index("ix_jobs_is_checked", table_name="jobs")
    op.drop_index("ix_companies_is_checked", table_name="companies")
    op.drop_column("jobs", "is_checked")
    op.drop_column("companies", "is_checked")
