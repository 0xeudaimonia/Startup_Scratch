from __future__ import annotations

from datetime import datetime

import httpx

from common.config import settings
from models.raw_company import RawCompany
from sources.base import SourceDisabledError, StartupSource


PRODUCT_HUNT_POSTS = """
query Posts($first: Int!) {
  posts(first: $first, order: NEWEST) {
    edges {
      node {
        id
        name
        tagline
        description
        url
        website
        createdAt
        topics { edges { node { name } } }
      }
    }
  }
}
"""

TOKEN_URL = "https://api.producthunt.com/v2/oauth/token"
GRAPHQL_URL = "https://api.producthunt.com/v2/api/graphql"


class ProductHuntSource(StartupSource):
    name = "producthunt"
    category = "launch_platforms"
    requires = "PRODUCT_HUNT_API_KEY + PRODUCT_HUNT_API_SECRET (or PRODUCT_HUNT_TOKEN)"
    description = "Product Hunt GraphQL API for newly launched products."

    def is_enabled(self) -> bool:
        return bool(
            settings.product_hunt_token
            or (settings.product_hunt_api_key and settings.product_hunt_api_secret)
        )

    async def _access_token(self, client: httpx.AsyncClient) -> str:
        if settings.product_hunt_token:
            return settings.product_hunt_token
        if not (settings.product_hunt_api_key and settings.product_hunt_api_secret):
            raise SourceDisabledError(
                "Product Hunt requires PRODUCT_HUNT_API_KEY and PRODUCT_HUNT_API_SECRET "
                "from https://www.producthunt.com/v2/oauth/applications"
            )
        response = await client.post(
            TOKEN_URL,
            json={
                "client_id": settings.product_hunt_api_key,
                "client_secret": settings.product_hunt_api_secret,
                "grant_type": "client_credentials",
            },
            headers={"User-Agent": settings.user_agent},
        )
        response.raise_for_status()
        token = response.json().get("access_token")
        if not token:
            raise SourceDisabledError("Product Hunt token exchange did not return access_token")
        return str(token)

    async def discover(self) -> list[RawCompany]:
        if not self.is_enabled():
            raise SourceDisabledError(self.requires or "Product Hunt credentials missing")
        async with httpx.AsyncClient(timeout=30.0) as client:
            token = await self._access_token(client)
            response = await client.post(
                GRAPHQL_URL,
                headers={
                    "Authorization": f"Bearer {token}",
                    "User-Agent": settings.user_agent,
                },
                json={"query": PRODUCT_HUNT_POSTS, "variables": {"first": 20}},
            )
            response.raise_for_status()
            payload = response.json()
        companies: list[RawCompany] = []
        for edge in payload.get("data", {}).get("posts", {}).get("edges", []):
            node = edge.get("node") or {}
            website = node.get("website")
            if not website:
                continue
            topics = [
                t.get("node", {}).get("name")
                for t in (node.get("topics") or {}).get("edges") or []
            ]
            created = node.get("createdAt")
            launch_date = (
                datetime.fromisoformat(created.replace("Z", "+00:00")).date() if created else None
            )
            companies.append(
                RawCompany(
                    external_id=str(node.get("id")),
                    source_name=self.name,
                    source_url=node.get("url"),
                    confidence=0.75,
                    name=node.get("name") or "Unknown",
                    short_description=node.get("tagline"),
                    description=node.get("description") or node.get("tagline"),
                    website_url=website,
                    product_hunt_url=node.get("url"),
                    categories=[t for t in topics if t],
                    keywords=[t for t in topics if t],
                    product_launch_date=launch_date,
                    source_urls=[node.get("url")] if node.get("url") else [],
                    raw_payload=node,
                )
            )
        return companies
