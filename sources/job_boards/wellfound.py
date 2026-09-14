from __future__ import annotations

from sources.base import SourceDisabledError, StartupSource
from models.raw_company import RawCompany


class WellfoundSource(StartupSource):
    name = "wellfound"
    category = "job_boards"
    enabled = False
    requires = "official API / partnership"
    description = (
        "Wellfound (AngelList Talent) public HTML is protected and ToS-restricted. "
        "Enable this adapter only with an official data partnership or API."
    )

    def is_enabled(self) -> bool:
        return False

    async def discover(self) -> list[RawCompany]:
        raise SourceDisabledError(
            "Wellfound scraping is disabled. Use an official API or partnership; "
            "do not bypass authentication, CAPTCHA, or anti-bot protections."
        )
