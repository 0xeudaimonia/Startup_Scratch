from __future__ import annotations

from sources.accelerators.ycombinator import YCombinatorSource
from sources.base import StartupSource
from sources.funding.dealroom import DealroomSource
from sources.funding.growthlist import GrowthListSource
from sources.job_boards.wellfound import WellfoundSource
from sources.job_boards.yc_jobs import YCJobsSource
from sources.launch_platforms.hackernews import HackerNewsLaunchSource
from sources.launch_platforms.producthunt import ProductHuntSource
from sources.news.techcrunch import EUStartupsSource, SiftedSource, TechCrunchSource
from sources.startup_directories.f6s import F6SSource
from sources.startup_directories.fixture import FixtureSource
from sources.venture_capital.portfolios import (
    AccelSource,
    AndreessenHorowitzSource,
    AntlerSource,
    BessemerSource,
    GeneralCatalystSource,
    IndexVenturesSource,
    LightspeedSource,
    SeedcampSource,
    SequoiaSource,
    TechstarsSource,
)


def all_sources() -> list[StartupSource]:
    return [
        FixtureSource(),
        F6SSource(),
        YCombinatorSource(),
        ProductHuntSource(),
        HackerNewsLaunchSource(),
        TechCrunchSource(),
        EUStartupsSource(),
        SiftedSource(),
        DealroomSource(),
        GrowthListSource(),
        WellfoundSource(),
        YCJobsSource(),
        SequoiaSource(),
        AccelSource(),
        IndexVenturesSource(),
        AndreessenHorowitzSource(),
        GeneralCatalystSource(),
        BessemerSource(),
        LightspeedSource(),
        SeedcampSource(),
        AntlerSource(),
        TechstarsSource(),
    ]


def get_source(name: str) -> StartupSource:
    for source in all_sources():
        if source.name == name:
            return source
    raise KeyError(f"Unknown source: {name}")


def sources_by_category(category: str) -> list[StartupSource]:
    return [source for source in all_sources() if source.category == category]
