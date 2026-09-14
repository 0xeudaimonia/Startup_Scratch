from __future__ import annotations

from common.config import settings
from sources.base import SourceDisabledError, StartupSource
from models.raw_company import RawCompany


class DealroomSource(StartupSource):
    name = "dealroom"
    category = "funding"
    enabled = False
    requires = "DEALROOM_API_KEY"
    description = (
        "Dealroom adapter is disabled until an official API key is provided. "
        "See https://dealroom.co/ for API access."
    )

    def is_enabled(self) -> bool:
        return bool(settings.dealroom_api_key)

    async def discover(self) -> list[RawCompany]:
        raise SourceDisabledError(
            "Dealroom requires DEALROOM_API_KEY and a licensed API agreement. "
            "This adapter does not scrape the Dealroom website."
        )
