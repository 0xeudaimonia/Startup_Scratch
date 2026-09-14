from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://startup_radar:startup_radar@localhost:5432/startup_radar"
    database_url_sync: str = "postgresql://startup_radar:startup_radar@localhost:5432/startup_radar"
    redis_url: str = "redis://localhost:6379/0"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"

    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    product_hunt_token: str | None = None
    product_hunt_api_key: str | None = None
    product_hunt_api_secret: str | None = None
    dealroom_api_key: str | None = None

    user_agent: str = "StartupRadarBot/1.0 (+https://github.com/startup-radar)"
    scraper_concurrency: int = 2
    scraper_request_delay_seconds: float = 2.0
    yc_max_companies: int = 25


settings = Settings()
