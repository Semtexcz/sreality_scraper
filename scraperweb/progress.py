"""Terminal progress reporting utilities for scraper CLI runs."""

from __future__ import annotations

from collections.abc import Callable


DEFAULT_PROGRESS_REPORT_INTERVAL = 10


class ScrapeProgressReporter:
    """Provide hook methods for operator-visible scraper progress events."""

    def scrape_started(
        self,
        *,
        regions: tuple[str, ...],
        max_pages: int | None,
        max_estates: int | None,
    ) -> None:
        """Report the beginning of one top-level scrape run."""

    def region_started(self, *, region_slug: str) -> None:
        """Report the beginning of one region traversal."""

    def listing_page_started(self, *, region_slug: str, page_number: int) -> None:
        """Report the beginning of one listing-page fetch."""

    def listing_page_completed(
        self,
        *,
        region_slug: str,
        page_number: int,
        discovered_estates: int,
    ) -> None:
        """Report the number of new estate URLs observed on one page."""

    def estate_processed(
        self,
        *,
        total_processed: int,
        max_estates: int | None,
        listing_url: str,
    ) -> None:
        """Report cumulative estate-processing progress."""

    def detail_http_error_skipped(
        self,
        *,
        region_slug: str,
        page_number: int,
        listing_url: str | None,
        message: str,
    ) -> None:
        """Report that one listing was skipped after a recoverable HTTP failure."""

    def detail_markup_error_skipped(
        self,
        *,
        region_slug: str,
        page_number: int,
        listing_url: str,
        message: str,
    ) -> None:
        """Report that one listing was skipped after a recoverable markup failure."""

    def region_completed(self, *, region_slug: str, processed_estates: int) -> None:
        """Report the end of one region traversal."""


class TerminalScrapeProgressReporter(ScrapeProgressReporter):
    """Emit concise scraper progress messages to a terminal-friendly sink."""

    def __init__(
        self,
        *,
        output: Callable[[str], None],
        verbose: bool = False,
        quiet: bool = False,
        report_interval: int = DEFAULT_PROGRESS_REPORT_INTERVAL,
    ) -> None:
        """Store terminal output preferences for one scraper run."""

        self._output = output
        self._verbose = verbose
        self._quiet = quiet
        self._report_interval = report_interval

    def scrape_started(
        self,
        *,
        regions: tuple[str, ...],
        max_pages: int | None,
        max_estates: int | None,
    ) -> None:
        """Show the selected runtime bounds before network work begins."""

        if self._quiet:
            return
        region_list = ", ".join(regions)
        max_pages_label = str(max_pages) if max_pages is not None else "unbounded"
        max_estates_label = str(max_estates) if max_estates is not None else "unbounded"
        self._output(
            "Starting scrape: "
            f"regions={region_list}, max_pages={max_pages_label}, max_estates={max_estates_label}",
        )

    def region_started(self, *, region_slug: str) -> None:
        """Show the beginning of one region traversal."""

        if self._quiet:
            return
        self._output(f"Region {region_slug}: starting")

    def listing_page_started(self, *, region_slug: str, page_number: int) -> None:
        """Show which listing page is currently being fetched."""

        if self._quiet:
            return
        self._output(f"Region {region_slug}: fetching page {page_number}")

    def listing_page_completed(
        self,
        *,
        region_slug: str,
        page_number: int,
        discovered_estates: int,
    ) -> None:
        """Show page-level discovery counts in verbose mode."""

        if self._quiet or not self._verbose:
            return
        self._output(
            f"Region {region_slug}: page {page_number} yielded "
            f"{discovered_estates} new listings",
        )

    def estate_processed(
        self,
        *,
        total_processed: int,
        max_estates: int | None,
        listing_url: str,
    ) -> None:
        """Show estate-level progress using concise or verbose terminal output."""

        if self._quiet:
            return
        max_estates_label = str(max_estates) if max_estates is not None else "unbounded"
        if self._verbose:
            self._output(
                f"Processed {total_processed}/{max_estates_label} estates: {listing_url}",
            )
            return
        if total_processed == 1 or total_processed % self._report_interval == 0:
            self._output(f"Processed {total_processed}/{max_estates_label} estates")

    def detail_http_error_skipped(
        self,
        *,
        region_slug: str,
        page_number: int,
        listing_url: str | None,
        message: str,
    ) -> None:
        """Show skipped-listing failures without requiring debug log visibility."""

        if self._quiet:
            return
        listing_label = listing_url or "<unknown>"
        self._output(
            f"Region {region_slug}: skipped listing on page {page_number} "
            f"({listing_label}) after HTTP failure: {message}",
        )

    def detail_markup_error_skipped(
        self,
        *,
        region_slug: str,
        page_number: int,
        listing_url: str,
        message: str,
    ) -> None:
        """Show skipped-listing markup failures without requiring debug logs."""

        if self._quiet:
            return
        self._output(
            f"Region {region_slug}: skipped listing on page {page_number} "
            f"({listing_url}) after markup failure: {message}",
        )

    def region_completed(self, *, region_slug: str, processed_estates: int) -> None:
        """Show the number of estates persisted from one region traversal."""

        if self._quiet:
            return
        self._output(
            f"Region {region_slug}: completed with {processed_estates} processed estates",
        )
