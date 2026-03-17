"""Tests for scraper runtime composition and region URL selection."""

from __future__ import annotations

from scraperweb.cli_runtime_options import build_runtime_cli_options
from scraperweb.estate_scraper import run_scraper


def test_run_scraper_uses_global_all_czechia_listing_url_by_default(monkeypatch) -> None:
    """Route the default CLI region selection to the global Czechia listing URL."""

    captured_calls: list[tuple[str, str]] = []

    class FakeAcquisitionService:
        """Capture region slug and district link selected by the runtime."""

        def __init__(self, *args, region_slug: str, **kwargs) -> None:
            """Store the selected region slug without invoking real collaborators."""

            self._region_slug = region_slug

        def collect_for_region(
            self,
            district_link: str,
            max_pages: int,
            max_estates: int,
            tracked_estates: int,
        ) -> int:
            """Capture the URL used for the selected region and stop immediately."""

            del max_pages, max_estates, tracked_estates
            captured_calls.append((self._region_slug, district_link))
            return 0

    monkeypatch.setattr("scraperweb.estate_scraper.RawAcquisitionService", FakeAcquisitionService)
    monkeypatch.setattr("scraperweb.estate_scraper.build_raw_record_repository", lambda options: object())

    processed_estates = run_scraper(build_runtime_cli_options())

    assert processed_estates == 0
    assert captured_calls == [
        ("all-czechia", "https://www.sreality.cz/hledani/prodej/byty?strana="),
    ]
