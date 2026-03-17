"""Tests for terminal scraper progress reporting."""

from __future__ import annotations

from scraperweb.progress import TerminalScrapeProgressReporter


def test_terminal_progress_reporter_emits_default_progress_messages() -> None:
    """Emit concise progress output that makes active scraper work visible."""

    messages: list[str] = []
    reporter = TerminalScrapeProgressReporter(output=messages.append)

    reporter.scrape_started(
        regions=("all-czechia",),
        max_pages=None,
        max_estates=100,
    )
    reporter.region_started(region_slug="all-czechia")
    reporter.listing_page_started(region_slug="all-czechia", page_number=1)
    reporter.estate_processed(
        total_processed=1,
        max_estates=100,
        listing_url="https://detail/1",
    )
    reporter.detail_http_error_skipped(
        region_slug="all-czechia",
        page_number=1,
        listing_url="https://detail/2",
        message="404",
    )
    reporter.region_completed(region_slug="all-czechia", processed_estates=1)

    assert messages == [
        "Starting scrape: regions=all-czechia, max_pages=unbounded, max_estates=100",
        "Region all-czechia: starting",
        "Region all-czechia: fetching page 1",
        "Processed 1/100 estates",
        "Region all-czechia: skipped listing on page 1 (https://detail/2) after HTTP failure: 404",
        "Region all-czechia: completed with 1 processed estates",
    ]


def test_terminal_progress_reporter_emits_verbose_messages() -> None:
    """Emit page and listing details when verbose mode is enabled."""

    messages: list[str] = []
    reporter = TerminalScrapeProgressReporter(output=messages.append, verbose=True)

    reporter.listing_page_completed(
        region_slug="all-czechia",
        page_number=4,
        discovered_estates=24,
    )
    reporter.estate_processed(
        total_processed=11,
        max_estates=100,
        listing_url="https://detail/11",
    )

    assert messages == [
        "Region all-czechia: page 4 yielded 24 new listings",
        "Processed 11/100 estates: https://detail/11",
    ]


def test_terminal_progress_reporter_suppresses_output_in_quiet_mode() -> None:
    """Suppress progress messages entirely when quiet mode is requested."""

    messages: list[str] = []
    reporter = TerminalScrapeProgressReporter(output=messages.append, quiet=True)

    reporter.scrape_started(
        regions=("all-czechia",),
        max_pages=5,
        max_estates=100,
    )
    reporter.region_started(region_slug="all-czechia")
    reporter.listing_page_started(region_slug="all-czechia", page_number=1)
    reporter.listing_page_completed(
        region_slug="all-czechia",
        page_number=1,
        discovered_estates=20,
    )
    reporter.estate_processed(
        total_processed=1,
        max_estates=100,
        listing_url="https://detail/1",
    )
    reporter.detail_http_error_skipped(
        region_slug="all-czechia",
        page_number=1,
        listing_url="https://detail/2",
        message="404",
    )
    reporter.region_completed(region_slug="all-czechia", processed_estates=1)

    assert messages == []
