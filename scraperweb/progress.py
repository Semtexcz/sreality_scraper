"""Terminal progress reporting utilities for scraper and batch CLI runs."""

from __future__ import annotations

from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import TYPE_CHECKING

import click


DEFAULT_PROGRESS_REPORT_INTERVAL = 10

if TYPE_CHECKING:
    from scraperweb.scraper.runtime import ListingPageStopDiagnostics


class ScrapeProgressReporter:
    """Provide hook methods for operator-visible scraper progress events."""

    def scrape_started(
        self,
        *,
        regions: tuple[str, ...],
        max_pages: int | None,
        max_estates: int | None,
        resume_existing: bool,
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

    def listing_traversal_stopped(
        self,
        *,
        region_slug: str,
        diagnostics: ListingPageStopDiagnostics,
    ) -> None:
        """Report why region traversal stopped on a specific listing page."""

    def estate_processed(
        self,
        *,
        total_processed: int,
        max_estates: int | None,
        listing_url: str,
    ) -> None:
        """Report cumulative estate-processing progress."""

    def existing_listing_skipped(
        self,
        *,
        region_slug: str,
        page_number: int,
        total_skipped: int,
        listing_url: str,
    ) -> None:
        """Report that one already-persisted listing was skipped in resume mode."""

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

    def region_completed(
        self,
        *,
        region_slug: str,
        processed_estates: int,
        skipped_existing_estates: int,
    ) -> None:
        """Report the end of one region traversal."""


class BatchWorkflowProgressReporter:
    """Provide hook methods for operator-visible batch workflow progress events."""

    def workflow_started(
        self,
        *,
        workflow_name: str,
        selection: str,
        total_records: int,
    ) -> None:
        """Report the beginning of one filesystem-backed batch workflow."""

    def record_processed(
        self,
        *,
        workflow_name: str,
        total_processed: int,
        total_records: int,
        listing_id: str,
    ) -> None:
        """Report cumulative batch-workflow record progress."""


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
        resume_existing: bool,
    ) -> None:
        """Show the selected runtime bounds before network work begins."""

        if self._quiet:
            return
        region_list = ", ".join(regions)
        max_pages_label = str(max_pages) if max_pages is not None else "unbounded"
        max_estates_label = str(max_estates) if max_estates is not None else "unbounded"
        resume_label = "enabled" if resume_existing else "disabled"
        self._output(
            "Starting scrape: "
            "regions="
            f"{region_list}, max_pages={max_pages_label}, "
            f"max_estates={max_estates_label}, resume_existing={resume_label}",
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

    def listing_traversal_stopped(
        self,
        *,
        region_slug: str,
        diagnostics: ListingPageStopDiagnostics,
    ) -> None:
        """Show stop diagnostics so operators can explain traversal termination."""

        if self._quiet:
            return
        repeated_from_label = (
            str(diagnostics.repeated_page_first_seen_at)
            if diagnostics.repeated_page_first_seen_at is not None
            else "none"
        )
        self._output(
            f"Region {region_slug}: stopping on page {diagnostics.page_number} "
            f"(reason={diagnostics.reason}, observed={diagnostics.observed_estates}, "
            f"new={diagnostics.new_estates}, stale_streak={diagnostics.consecutive_stale_pages}, "
            f"repeated_from_page={repeated_from_label})",
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

    def existing_listing_skipped(
        self,
        *,
        region_slug: str,
        page_number: int,
        total_skipped: int,
        listing_url: str,
    ) -> None:
        """Show resume-mode skips without spamming normal terminal output."""

        if self._quiet:
            return
        if self._verbose:
            self._output(
                f"Region {region_slug}: skipped existing listing on page {page_number} "
                f"({listing_url})",
            )
            return
        if total_skipped == 1 or total_skipped % self._report_interval == 0:
            self._output(f"Skipped {total_skipped} existing listings")

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

    def region_completed(
        self,
        *,
        region_slug: str,
        processed_estates: int,
        skipped_existing_estates: int,
    ) -> None:
        """Show the number of estates persisted from one region traversal."""

        if self._quiet:
            return
        self._output(
            f"Region {region_slug}: completed with {processed_estates} processed estates "
            f"and {skipped_existing_estates} skipped existing listings",
        )


class TerminalBatchWorkflowProgressReporter(BatchWorkflowProgressReporter):
    """Emit concise batch-workflow progress messages to a terminal-friendly sink."""

    def __init__(
        self,
        *,
        output: Callable[[str], None],
        verbose: bool = False,
        quiet: bool = False,
        report_interval: int = DEFAULT_PROGRESS_REPORT_INTERVAL,
    ) -> None:
        """Store terminal output preferences for one batch workflow run."""

        self._output = output
        self._verbose = verbose
        self._quiet = quiet
        self._report_interval = report_interval

    def workflow_started(
        self,
        *,
        workflow_name: str,
        selection: str,
        total_records: int,
    ) -> None:
        """Show the selected batch scope before record processing begins."""

        if self._quiet:
            return
        self._output(
            f"Starting {workflow_name}: scope={selection}, records={total_records}",
        )

    def record_processed(
        self,
        *,
        workflow_name: str,
        total_processed: int,
        total_records: int,
        listing_id: str,
    ) -> None:
        """Show cumulative batch-workflow progress with optional listing detail."""

        if self._quiet:
            return
        if self._verbose:
            self._output(
                f"{workflow_name.capitalize()} progress: "
                f"{total_processed}/{total_records} records ({listing_id})",
            )
            return
        if total_processed == 1 or total_processed % self._report_interval == 0:
            self._output(
                f"{workflow_name.capitalize()} progress: "
                f"{total_processed}/{total_records} records",
            )


class TerminalBatchWorkflowProgressBarReporter(BatchWorkflowProgressReporter):
    """Render batch-workflow progress as an in-place terminal progress bar."""

    def __init__(
        self,
        *,
        progressbar_factory: Callable[..., AbstractContextManager[click.ProgressBar[None]]] = (
            click.progressbar
        ),
    ) -> None:
        """Store the progress-bar factory used for one batch workflow run."""

        self._progressbar_factory = progressbar_factory
        self._progressbar_context: AbstractContextManager[click.ProgressBar[None]] | None = None
        self._progressbar: click.ProgressBar[None] | None = None

    def workflow_started(
        self,
        *,
        workflow_name: str,
        selection: str,
        total_records: int,
    ) -> None:
        """Open a terminal progress bar for the selected workflow scope."""

        del selection
        self._progressbar_context = self._progressbar_factory(
            length=total_records,
            label=f"{workflow_name.capitalize()} progress",
            show_pos=True,
        )
        self._progressbar = self._progressbar_context.__enter__()

    def record_processed(
        self,
        *,
        workflow_name: str,
        total_processed: int,
        total_records: int,
        listing_id: str,
    ) -> None:
        """Advance and close the terminal progress bar as records complete."""

        del workflow_name, listing_id
        if self._progressbar is None:
            return
        self._progressbar.update(1)
        if total_processed >= total_records:
            self._close_progressbar()

    def _close_progressbar(self) -> None:
        """Close an active progress bar and release the held context."""

        if self._progressbar_context is None:
            return
        self._progressbar_context.__exit__(None, None, None)
        self._progressbar_context = None
        self._progressbar = None

    def __del__(self) -> None:
        """Ensure partially used progress bars do not leak terminal state."""

        self._close_progressbar()
