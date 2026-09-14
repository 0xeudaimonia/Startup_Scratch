from alembic import op

from database.base import Base
from database.models import (  # noqa: F401
    Company,
    CompanyInvestor,
    CompanySource,
    DuplicateCandidate,
    FieldObservation,
    FundingRound,
    Investor,
    Job,
    SavedView,
    ScrapeRun,
    SourceRecord,
)

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
