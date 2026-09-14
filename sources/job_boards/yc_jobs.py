from __future__ import annotations

from sources.accelerators.ycombinator import YCombinatorSource


class YCJobsSource(YCombinatorSource):
    """YC companies currently hiring, using the public yc-oss hiring dataset."""

    name = "yc_jobs"
    category = "job_boards"
    description = "Y Combinator hiring companies from the public yc-oss hiring.json dataset."
