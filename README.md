# Startup Radar

Discover, normalize, score, and browse newly funded and remote-friendly startups.

This MVP runs locally with Docker Compose: PostgreSQL, Redis, FastAPI, Celery, and a Next.js dashboard. Seed data is loaded on first boot so the UI is usable immediately. A manual scraper button ingests new companies through the source-adapter pipeline.

## Quick start

```bash
cd startup-radar
cp .env.example .env
docker compose up --build
# If the Compose v2 plugin is missing:
docker-compose up --build
```

Then open:

- Web: [http://localhost:3000](http://localhost:3000) (or the port in `WEB_PORT`)
- API: [http://localhost:8000/docs](http://localhost:8000/docs) (or the port in `API_PORT`)
- Health: [http://localhost:8000/health](http://localhost:8000/health)

If ports 3000 or 8000 are already in use, set `WEB_PORT` and `API_PORT` in `.env`.

The first boot migrates the database, seeds 16 realistic companies, and starts the scheduler.

Postgres and Redis stay on the Docker network (not published to the host) so they do not collide with local databases. Override `WEB_PORT` and `API_PORT` in `.env` if 3000 or 8000 are already taken.

## What you can do

1. Browse the dashboard (new today, newly funded, recently founded, global remote, hiring engineers, top opportunities).
2. Search and filter companies.
3. Open a company detail page for website, funding, founding date, remote policy, jobs, tech, investors, sources, and opportunity score.
4. Run a scraper from **Sources** (start with `fixture`, which always creates a company discovered today).
5. Watch the new company appear on the dashboard.

## Architecture

```
apps/web          Next.js App Router dashboard
apps/api          FastAPI HTTP API
packages/database SQLAlchemy models + Alembic
packages/models   Pydantic RawCompany records
packages/scoring  Opportunity and growth scores
packages/common   URL, currency, funding, HTTP helpers
sources/          One adapter per data source
workers/          Celery ingest, enrichment, scoring
```

Every collector implements `StartupSource` and emits `RawCompany` records. Ingest handles normalization, deduplication, source tracing, and scoring.

## Scraping rules

Adapters prefer official APIs, RSS, and public structured JSON.

Enabled by default:

- `fixture` — deterministic demo source
- `ycombinator` / `yc_jobs` — public yc-oss JSON (not HTML scraping)
- `growthlist` — public [Growth List](https://growthlist.co/) sample tables (funded, pre-seed, seed, Series A/B, AI, SaaS, B2B, FinTech, e-commerce, US, San Francisco, Finland). Not the paid Google Sheets / member database.
- `hackernews` — HN Algolia API
- `techcrunch`, `eu_startups`, `sifted` — RSS feeds (articles are evidence, not canonical records)

Disabled until credentials or permission exist:

- Product Hunt (`PRODUCT_HUNT_TOKEN`)
- Dealroom (`DEALROOM_API_KEY`)
- Wellfound, F6S, and VC portfolio sites

The project does not bypass authentication, CAPTCHA, Cloudflare, paywalls, or rate limits, and it does not rotate proxies.

## Manual scrape

From the Sources page, or:

```bash
docker compose exec api python scripts/run_scraper.py --source fixture
docker compose exec api python scripts/run_scraper.py --source ycombinator
docker compose exec api python scripts/run_scraper.py --source growthlist
```

Celery Beat also runs funding/news/launch/enrichment jobs on a schedule.

## Tests

```bash
pip install -e ".[dev]"
pytest
```

Coverage includes domain normalization, funding/currency parsing, remote detection, opportunity scoring, job/tech extraction, and source adapters.

## Environment

See `.env.example`. Important variables:

- `DATABASE_URL` / `DATABASE_URL_SYNC`
- `REDIS_URL`
- `USER_AGENT`
- `SCRAPER_CONCURRENCY`
- `OPENAI_API_KEY` (optional LLM fallback)
- `PRODUCT_HUNT_TOKEN` (optional)
- `DEALROOM_API_KEY` (optional)

## Implementation phases

Phase 1 (this MVP): Docker, schema, company API, dashboard, seed data, adapter interface, scoring, manual scrape.

Later phases add more live sources, website enrichment depth, and additional VC coverage — without changing the ingest contract.
