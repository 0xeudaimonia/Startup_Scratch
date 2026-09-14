from __future__ import annotations

from common.config import settings


class LLMClient:
    """OpenAI-compatible client used only as an optional enrichment fallback."""

    def __init__(self) -> None:
        self.api_key = settings.openai_api_key
        self.base_url = settings.openai_base_url
        self.model = settings.openai_model

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    async def complete(self, prompt: str) -> str | None:
        if not self.enabled:
            return None
        import httpx

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0,
                },
            )
            response.raise_for_status()
            payload = response.json()
        return payload["choices"][0]["message"]["content"]
