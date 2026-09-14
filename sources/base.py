from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod

from models.raw_company import RawCompany


class SourceDisabledError(RuntimeError):
    """Raised when a source cannot run without credentials or permission."""


class StartupSource(ABC):
    name: str
    category: str = "other"
    enabled: bool = True
    requires: str | None = None
    description: str = ""

    def is_enabled(self) -> bool:
        return self.enabled

    @abstractmethod
    async def discover(self) -> list[RawCompany]:
        """Return newly discovered normalized company records."""

    async def get_company(self, external_id: str) -> RawCompany | None:
        for company in await self.discover():
            if company.external_id == external_id:
                return company
        return None
