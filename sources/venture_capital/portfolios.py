from __future__ import annotations

from sources.base import SourceDisabledError, StartupSource
from models.raw_company import RawCompany


class DisabledVcPortfolioSource(StartupSource):
    category = "venture_capital"
    enabled = False
    portfolio_url: str = ""

    def is_enabled(self) -> bool:
        return False

    async def discover(self) -> list[RawCompany]:
        raise SourceDisabledError(
            f"{self.name} portfolio pages are typically JavaScript-rendered and ToS-restricted. "
            f"Official portfolio URL: {self.portfolio_url}. Enable only with a public API, RSS, "
            "or explicit permission. This adapter will not bypass bot protection."
        )


class SequoiaSource(DisabledVcPortfolioSource):
    name = "sequoia"
    portfolio_url = "https://www.sequoiacap.com/companies/"
    description = "Disabled Sequoia portfolio adapter. Needs official data access."


class AccelSource(DisabledVcPortfolioSource):
    name = "accel"
    portfolio_url = "https://www.accel.com/companies"
    description = "Disabled Accel portfolio adapter. Needs official data access."


class IndexVenturesSource(DisabledVcPortfolioSource):
    name = "index_ventures"
    portfolio_url = "https://www.indexventures.com/companies/"
    description = "Disabled Index Ventures portfolio adapter. Needs official data access."


class AndreessenHorowitzSource(DisabledVcPortfolioSource):
    name = "andreessen_horowitz"
    portfolio_url = "https://a16z.com/portfolio/"
    description = "Disabled a16z portfolio adapter. Needs official data access."


class GeneralCatalystSource(DisabledVcPortfolioSource):
    name = "general_catalyst"
    portfolio_url = "https://www.generalcatalyst.com/portfolio"
    description = "Disabled General Catalyst portfolio adapter. Needs official data access."


class BessemerSource(DisabledVcPortfolioSource):
    name = "bessemer"
    portfolio_url = "https://www.bvp.com/portfolio"
    description = "Disabled Bessemer portfolio adapter. Needs official data access."


class LightspeedSource(DisabledVcPortfolioSource):
    name = "lightspeed"
    portfolio_url = "https://lsvp.com/companies/"
    description = "Disabled Lightspeed portfolio adapter. Needs official data access."


class SeedcampSource(DisabledVcPortfolioSource):
    name = "seedcamp"
    portfolio_url = "https://seedcamp.com/portfolio/"
    description = "Disabled Seedcamp portfolio adapter. Needs official data access."


class AntlerSource(DisabledVcPortfolioSource):
    name = "antler"
    portfolio_url = "https://www.antler.co/portfolio"
    description = "Disabled Antler portfolio adapter. Needs official data access."


class TechstarsSource(DisabledVcPortfolioSource):
    name = "techstars"
    portfolio_url = "https://www.techstars.com/portfolio"
    description = "Disabled Techstars portfolio adapter. Public API/permission required."
