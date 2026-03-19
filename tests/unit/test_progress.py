"""Tests for terminal scraper progress reporting."""

from __future__ import annotations

from scraperweb.progress import TerminalScrapeProgressReporter
from scraperweb.scraper.runtime import ListingPageStopDiagnostics


def test_terminal_progress_reporter_emits_default_progress_messages() -> None:
    """Emit concise progress output that makes active scraper work visible."""

    messages: list[str] = []
    reporter = TerminalScrapeProgressReporter(output=messages.append)

    reporter.scrape_started(
        regions=("all-czechia",),
        max_pages=None,
        max_estates=100,
        resume_existing=True,
    )
    reporter.region_started(region_slug="all-czechia")
    reporter.listing_page_started(region_slug="all-czechia", page_number=1)
    reporter.existing_listing_skipped(
        region_slug="all-czechia",
        page_number=1,
        total_skipped=1,
        listing_url="https://detail/existing",
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
    reporter.detail_markup_error_skipped(
        region_slug="all-czechia",
        page_number=1,
        listing_url="https://detail/3",
        message="missing non-empty listing title",
    )
    reporter.region_completed(
        region_slug="all-czechia",
        processed_estates=1,
        skipped_existing_estates=1,
    )

    assert messages == [
        "Starting scrape: regions=all-czechia, max_pages=unbounded, max_estates=100, resume_existing=enabled",
        "Region all-czechia: starting",
        "Region all-czechia: fetching page 1",
        "Skipped 1 existing listings",
        "Processed 1/100 estates",
        "Region all-czechia: skipped listing on page 1 (https://detail/2) after HTTP failure: 404",
        "Region all-czechia: skipped listing on page 1 (https://detail/3) after markup failure: missing non-empty listing title",
        "Region all-czechia: completed with 1 processed estates and 1 skipped existing listings",
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
    reporter.existing_listing_skipped(
        region_slug="all-czechia",
        page_number=4,
        total_skipped=3,
        listing_url="https://detail/existing",
    )
    reporter.estate_processed(
        total_processed=11,
        max_estates=100,
        listing_url="https://detail/11",
    )
    reporter.listing_traversal_stopped(
        region_slug="all-czechia",
        diagnostics=ListingPageStopDiagnostics(
            reason="stale_listing_window_limit",
            page_number=307,
            observed_estates=24,
            new_estates=0,
            consecutive_stale_pages=3,
            repeated_page_first_seen_at=None,
        ),
    )

    assert messages == [
        "Region all-czechia: page 4 yielded 24 new listings",
        "Region all-czechia: skipped existing listing on page 4 (https://detail/existing)",
        "Processed 11/100 estates: https://detail/11",
        "Region all-czechia: stopping on page 307 (reason=stale_listing_window_limit, observed=24, new=0, stale_streak=3, repeated_from_page=none)",
    ]


def test_terminal_progress_reporter_suppresses_output_in_quiet_mode() -> None:
    """Suppress progress messages entirely when quiet mode is requested."""

    messages: list[str] = []
    reporter = TerminalScrapeProgressReporter(output=messages.append, quiet=True)

    reporter.scrape_started(
        regions=("all-czechia",),
        max_pages=5,
        max_estates=100,
        resume_existing=False,
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
    reporter.existing_listing_skipped(
        region_slug="all-czechia",
        page_number=1,
        total_skipped=1,
        listing_url="https://detail/existing",
    )
    reporter.detail_http_error_skipped(
        region_slug="all-czechia",
        page_number=1,
        listing_url="https://detail/2",
        message="404",
    )
    reporter.detail_markup_error_skipped(
        region_slug="all-czechia",
        page_number=1,
        listing_url="https://detail/3",
        message="missing title",
    )
    reporter.listing_traversal_stopped(
        region_slug="all-czechia",
        diagnostics=ListingPageStopDiagnostics(
            reason="empty_listing_page",
            page_number=2,
            observed_estates=0,
            new_estates=0,
            consecutive_stale_pages=0,
            repeated_page_first_seen_at=None,
        ),
    )
    reporter.region_completed(
        region_slug="all-czechia",
        processed_estates=1,
        skipped_existing_estates=1,
    )

    assert messages == []


def test_terminal_progress_reporter_labels_unbounded_estate_limit_explicitly() -> None:
    """Render unbounded estate processing clearly in operator-visible output."""

    messages: list[str] = []
    reporter = TerminalScrapeProgressReporter(output=messages.append, verbose=True)

    reporter.scrape_started(
        regions=("all-czechia",),
        max_pages=None,
        max_estates=None,
        resume_existing=False,
    )
    reporter.estate_processed(
        total_processed=3,
        max_estates=None,
        listing_url="https://detail/3",
    )

    assert messages == [
        "Starting scrape: regions=all-czechia, max_pages=unbounded, max_estates=unbounded, resume_existing=disabled",
        "Processed 3/unbounded estates: https://detail/3",
    ]
