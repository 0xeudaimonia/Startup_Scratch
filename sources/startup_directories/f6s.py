from __future__ import annotations

from sources.base import SourceDisabledError, StartupSource
from models.raw_company import RawCompany


class F6SSource(StartupSource):
    name = "f6s"
    category = "startup_directories"
    enabled = False
    requires = "official API"
    description = (
        "F6S directory scraping is disabled. Use the official F6S API or a data partnership."
    )

    def is_enabled(self) -> bool:
        return False

    async def discover(self) -> list[RawCompany]:
        raise SourceDisabledError("F6S requires an official API. HTML scraping is not enabled.")
