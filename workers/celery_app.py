from __future__ import annotations

from celery.schedules import crontab

from workers.celery_impl import celery_app

celery_app.conf.beat_schedule = {
    "funding-sources": {
        "task": "workers.scraping.tasks.run_category",
        "schedule": crontab(minute=0, hour="*/2"),
        "args": ("funding",),
    },
    "news-sources": {
        "task": "workers.scraping.tasks.run_category",
        "schedule": crontab(minute=20, hour="*/2"),
        "args": ("news",),
    },
    "launch-sources": {
        "task": "workers.scraping.tasks.run_category",
        "schedule": crontab(minute=0, hour="*/4"),
        "args": ("launch_platforms",),
    },
    "accelerator-sources": {
        "task": "workers.scraping.tasks.run_source",
        "schedule": crontab(minute=30, hour="*/4"),
        "args": ("ycombinator",),
    },
    "jobs-sources": {
        "task": "workers.scraping.tasks.run_category",
        "schedule": crontab(minute=0, hour="*/12"),
        "args": ("job_boards",),
    },
    "company-enrichment": {
        "task": "workers.enrichment.tasks.enrich_stale_companies",
        "schedule": crontab(minute=15, hour=3),
    },
    "company-refresh": {
        "task": "workers.scoring.tasks.rescore_all",
        "schedule": crontab(minute=0, hour=4, day_of_week="*/3"),
    },
    "inactive-cleanup": {
        "task": "workers.scraping.tasks.mark_stale_jobs",
        "schedule": crontab(minute=0, hour=5, day_of_week="sun"),
    },
}

__all__ = ["celery_app"]
