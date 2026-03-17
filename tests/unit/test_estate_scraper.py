"""Tests for scraper runtime composition and region URL selection."""

from __future__ import annotations

from scraperweb.cli_runtime_options import build_runtime_cli_options
from scraperweb.estate_scraper import run_scraper


def test_run_scraper_uses_global_all_czechia_listing_url_by_default(monkeypatch) -> None:
    """Route the default CLI region selection to the global Czechia listing URL."""

    captured_calls: list[tuple[str, str, int | None]] = []

    class FakeAcquisitionService:
        """Capture region slug and district link selected by the runtime."""

        def __init__(self, *args, region_slug: str, **kwargs) -> None:
            """Store the selected region slug without invoking real collaborators."""

            self._region_slug = region_slug

        def collect_for_region(
            self,
            district_link: str,
            max_pages: int | None,
            max_estates: int,
            tracked_estates: int,
        ) -> int:
            """Capture the URL used for the selected region and stop immediately."""

            captured_calls.append((self._region_slug, district_link, max_pages))
            del max_estates, tracked_estates
            return 0

    monkeypatch.setattr("scraperweb.estate_scraper.RawAcquisitionService", FakeAcquisitionService)
    monkeypatch.setattr("scraperweb.estate_scraper.build_raw_record_repository", lambda options: object())

    processed_estates = run_scraper(build_runtime_cli_options())

    assert processed_estates == 0
    assert captured_calls == [
        ("all-czechia", "https://www.sreality.cz/hledani/prodej/byty?strana=", None),
    ]


def test_run_scraper_passes_fail_fast_http_mode_to_acquisition_service(monkeypatch) -> None:
    """Compose acquisition services with the configured HTTP failure mode."""

    captured_fail_modes: list[bool] = []

    class FakeAcquisitionService:
        """Capture the configured fail-fast flag without running scraper work."""

        def __init__(self, *args, fail_on_http_error: bool, **kwargs) -> None:
            """Store the HTTP failure mode passed by runtime composition."""

            captured_fail_modes.append(fail_on_http_error)

        def collect_for_region(
            self,
            district_link: str,
            max_pages: int | None,
            max_estates: int,
            tracked_estates: int,
        ) -> int:
            """Stop immediately after the first captured composition call."""

            del district_link, max_pages, max_estates, tracked_estates
            return 0

    monkeypatch.setattr("scraperweb.estate_scraper.RawAcquisitionService", FakeAcquisitionService)
    monkeypatch.setattr("scraperweb.estate_scraper.build_raw_record_repository", lambda options: object())

    processed_estates = run_scraper(build_runtime_cli_options(fail_on_http_error=True))

    assert processed_estates == 0
    assert captured_fail_modes == [True]
