"""Scraper-stage runtime services that emit raw listing contracts."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import datetime, timezone
from itertools import count
from typing import Callable

from loguru import logger

from scraperweb.cli_runtime_options import ALL_CZECHIA_REGION
from scraperweb.progress import ScrapeProgressReporter
from scraperweb.scraper.clients import DetailPageClient, ListingPageClient
from scraperweb.scraper.exceptions import (
    ScraperHttpError,
    ScraperMarkupError,
    ScraperResponseError,
    ScraperTransportError,
)
from scraperweb.scraper.models import (
    DetailMarkupFailureArtifact,
    JsonValue,
    RawListingRecord,
    RawSourceMetadata,
)
from scraperweb.scraper.parsers import SrealityDetailPageParser, SrealityListingPageParser

DETAIL_PAGE_PARSER_VERSION = "sreality-detail-v1"
DETAIL_PAGE_HTTP_STATUS = 200
DETAIL_PAGE_CAPTURED_FROM = "detail_page"
ALL_CZECHIA_STALE_PAGE_LIMIT = 3


@dataclass(frozen=True)
class ListingPageStopDiagnostics:
    """Describe why one listing traversal stopped on a specific page."""

    reason: str
    page_number: int
    observed_estates: int
    new_estates: int
    consecutive_stale_pages: int
    repeated_page_first_seen_at: int | None = None


@dataclass(frozen=True)
class ListingPageEvaluationResult:
    """Capture the outcome of evaluating one listing page."""

    should_continue: bool
    new_estate_urls: list[str]
    stop_diagnostics: ListingPageStopDiagnostics | None = None


@dataclass
class ListingTraversalState:
    """Track observed listing-page outcomes during one region traversal."""

    seen_page_signatures: dict[tuple[str, ...], int] = field(default_factory=dict)
    seen_estate_urls: set[str] = field(default_factory=set)
    consecutive_stale_pages: int = 0


class RawListingCollector:
    """Collect raw listing records from listing and detail page HTML.

    Region traversal can be bounded by ``max_pages`` when an explicit limit is
    provided. It also stops early when a listing page is empty, repeats an
    already observed estate URL set, or contains no estate URLs that were not
    already seen in the same region traversal.
    """

    def __init__(
        self,
        listing_page_client: ListingPageClient,
        detail_page_client: DetailPageClient,
        listing_page_parser: SrealityListingPageParser,
        detail_page_parser: SrealityDetailPageParser,
        region_slug: str,
        scrape_run_id: str,
        capture_raw_page_snapshots: bool = False,
        fail_on_detail_http_error: bool = False,
        progress_reporter: ScrapeProgressReporter | None = None,
        existing_listing_checker: Callable[[str, str], bool] | None = None,
        markup_failure_artifact_handler: (
            Callable[[DetailMarkupFailureArtifact], None] | None
        ) = None,
    ) -> None:
        """Store collaborators used to build scraper-owned raw contracts."""

        self._listing_page_client = listing_page_client
        self._detail_page_client = detail_page_client
        self._listing_page_parser = listing_page_parser
        self._detail_page_parser = detail_page_parser
        self._region_slug = region_slug
        self._scrape_run_id = scrape_run_id
        self._capture_raw_page_snapshots = capture_raw_page_snapshots
        self._fail_on_detail_http_error = fail_on_detail_http_error
        self._progress_reporter = progress_reporter or ScrapeProgressReporter()
        self._existing_listing_checker = existing_listing_checker
        self._markup_failure_artifact_handler = markup_failure_artifact_handler
        self._skipped_existing_listings = 0

    @property
    def skipped_existing_listings(self) -> int:
        """Return how many already-persisted listings were skipped in the last run."""

        return self._skipped_existing_listings

    def collect_region_records(
        self,
        district_link: str,
        max_pages: int | None,
    ) -> Iterator[RawListingRecord]:
        """Yield raw listing records for one region until traversal exhaustion."""

        self._skipped_existing_listings = 0
        traversal_state = ListingTraversalState()
        page_numbers = range(1, max_pages + 1) if max_pages is not None else count(1)
        use_hardened_all_czechia_traversal = self._should_harden_all_czechia_traversal(
            max_pages=max_pages,
        )

        for page_number in page_numbers:
            listing_url = f"{district_link}{page_number}"
            self._progress_reporter.listing_page_started(
                region_slug=self._region_slug,
                page_number=page_number,
            )
            listing_html = self._fetch_listing_page(
                listing_url=listing_url,
                page_number=page_number,
            )
            try:
                estate_urls = self._listing_page_parser.parse_estate_urls(listing_html)
            except ScraperMarkupError as error:
                raise self._build_markup_response_error(
                    error=error,
                    request_url=listing_url,
                    page_number=page_number,
                    listing_url=None,
                ) from error

            evaluation_result = self._evaluate_listing_page(
                estate_urls=estate_urls,
                page_number=page_number,
                traversal_state=traversal_state,
                use_hardened_all_czechia_traversal=use_hardened_all_czechia_traversal,
            )
            if not evaluation_result.should_continue:
                assert evaluation_result.stop_diagnostics is not None
                self._report_listing_traversal_stop(
                    diagnostics=evaluation_result.stop_diagnostics,
                )
                return
            self._progress_reporter.listing_page_completed(
                region_slug=self._region_slug,
                page_number=page_number,
                discovered_estates=len(evaluation_result.new_estate_urls),
            )

            for estate_url in evaluation_result.new_estate_urls:
                listing_id = self._extract_listing_id(estate_url)
                if self._existing_listing_checker is not None and self._existing_listing_checker(
                    listing_id,
                    estate_url,
                ):
                    self._skipped_existing_listings += 1
                    self._progress_reporter.existing_listing_skipped(
                        region_slug=self._region_slug,
                        page_number=page_number,
                        total_skipped=self._skipped_existing_listings,
                        listing_url=estate_url,
                    )
                    continue
                try:
                    detail_html = self._fetch_detail_page(
                        detail_url=estate_url,
                        page_number=page_number,
                    )
                except ScraperHttpError as error:
                    if self._fail_on_detail_http_error:
                        raise
                    logger.error(
                        "Skipping listing after scraper HTTP failure for region={} page={} listing_url={} request_url={}: {}",
                        error.region_slug,
                        error.listing_page_number,
                        error.listing_url,
                        error.request_url,
                        error.message,
                    )
                    self._progress_reporter.detail_http_error_skipped(
                        region_slug=error.region_slug or self._region_slug,
                        page_number=error.listing_page_number or page_number,
                        listing_url=error.listing_url,
                        message=error.message,
                    )
                    continue
                try:
                    raw_payload = self._detail_page_parser.parse_raw_payload(detail_html)
                except ScraperMarkupError as error:
                    markup_error = self._build_markup_response_error(
                        error=error,
                        request_url=estate_url,
                        page_number=page_number,
                        listing_url=estate_url,
                    )
                    self._persist_markup_failure_artifact(
                        estate_url=estate_url,
                        page_number=page_number,
                        detail_html=detail_html,
                        failure_message=error.message,
                    )
                    if self._fail_on_detail_http_error:
                        raise markup_error from error
                    logger.error(
                        "Skipping listing after scraper markup failure for region={} page={} listing_url={} request_url={}: {}",
                        markup_error.region_slug,
                        markup_error.listing_page_number,
                        markup_error.listing_url,
                        markup_error.request_url,
                        markup_error.message,
                    )
                    self._progress_reporter.detail_markup_error_skipped(
                        region_slug=markup_error.region_slug or self._region_slug,
                        page_number=markup_error.listing_page_number or page_number,
                        listing_url=estate_url,
                        message=markup_error.message,
                    )
                    continue
                yield self._build_raw_listing_record(
                    estate_url=estate_url,
                    listing_id=listing_id,
                    page_number=page_number,
                    raw_payload=raw_payload,
                    detail_html=detail_html,
                )

    def _evaluate_listing_page(
        self,
        estate_urls: list[str],
        page_number: int,
        traversal_state: ListingTraversalState,
        use_hardened_all_czechia_traversal: bool,
    ) -> ListingPageEvaluationResult:
        """Return whether traversal should continue and which estate URLs are new."""

        if not estate_urls:
            return ListingPageEvaluationResult(
                should_continue=False,
                new_estate_urls=[],
                stop_diagnostics=ListingPageStopDiagnostics(
                    reason="empty_listing_page",
                    page_number=page_number,
                    observed_estates=0,
                    new_estates=0,
                    consecutive_stale_pages=traversal_state.consecutive_stale_pages,
                ),
            )

        page_signature = tuple(estate_urls)
        new_estate_urls = [
            estate_url
            for estate_url in estate_urls
            if estate_url not in traversal_state.seen_estate_urls
        ]
        if not new_estate_urls:
            traversal_state.consecutive_stale_pages += 1
            repeated_page_first_seen_at = traversal_state.seen_page_signatures.get(
                page_signature,
            )
            should_stop_for_stale_window = (
                not use_hardened_all_czechia_traversal
                or repeated_page_first_seen_at is not None
                or traversal_state.consecutive_stale_pages >= ALL_CZECHIA_STALE_PAGE_LIMIT
            )
            traversal_state.seen_page_signatures.setdefault(page_signature, page_number)
            if should_stop_for_stale_window:
                return ListingPageEvaluationResult(
                    should_continue=False,
                    new_estate_urls=[],
                    stop_diagnostics=ListingPageStopDiagnostics(
                        reason=(
                            "repeated_listing_page_signature"
                            if repeated_page_first_seen_at is not None
                            else "stale_listing_window_limit"
                        ),
                        page_number=page_number,
                        observed_estates=len(estate_urls),
                        new_estates=0,
                        consecutive_stale_pages=traversal_state.consecutive_stale_pages,
                        repeated_page_first_seen_at=repeated_page_first_seen_at,
                    ),
                )
            return ListingPageEvaluationResult(
                should_continue=True,
                new_estate_urls=[],
            )

        traversal_state.consecutive_stale_pages = 0
        traversal_state.seen_page_signatures.setdefault(page_signature, page_number)
        traversal_state.seen_estate_urls.update(new_estate_urls)
        return ListingPageEvaluationResult(
            should_continue=True,
            new_estate_urls=new_estate_urls,
        )

    def _should_harden_all_czechia_traversal(self, max_pages: int | None) -> bool:
        """Return whether duplicate-window tolerance should be enabled."""

        return self._region_slug == ALL_CZECHIA_REGION and max_pages is None

    def _report_listing_traversal_stop(
        self,
        diagnostics: ListingPageStopDiagnostics,
    ) -> None:
        """Emit operator-visible diagnostics for one listing traversal stop."""

        logger.info(
            "Stopping listing traversal for region={} on page={} reason={} observed_estates={} "
            "new_estates={} consecutive_stale_pages={} repeated_page_first_seen_at={}",
            self._region_slug,
            diagnostics.page_number,
            diagnostics.reason,
            diagnostics.observed_estates,
            diagnostics.new_estates,
            diagnostics.consecutive_stale_pages,
            diagnostics.repeated_page_first_seen_at,
        )
        self._progress_reporter.listing_traversal_stopped(
            region_slug=self._region_slug,
            diagnostics=diagnostics,
        )

    def _fetch_listing_page(self, listing_url: str, page_number: int) -> str:
        """Fetch one listing page and attach region and page context to failures."""

        try:
            return self._listing_page_client.fetch(listing_url)
        except ScraperHttpError as error:
            raise self._enrich_http_error(
                error=error,
                page_number=page_number,
                listing_url=None,
            ) from error

    def _fetch_detail_page(self, detail_url: str, page_number: int) -> str:
        """Fetch one detail page and attach region, page, and listing URL context."""

        try:
            return self._detail_page_client.fetch(detail_url)
        except ScraperHttpError as error:
            raise self._enrich_http_error(
                error=error,
                page_number=page_number,
                listing_url=detail_url,
            ) from error

    def _enrich_http_error(
        self,
        error: ScraperHttpError,
        page_number: int,
        listing_url: str | None,
    ) -> ScraperHttpError:
        """Return a same-category scraper error enriched with collector context."""

        if isinstance(error, ScraperTransportError):
            return ScraperTransportError(
                message=error.message,
                request_url=error.request_url,
                timeout_seconds=error.timeout_seconds,
                attempts=error.attempts,
                region_slug=self._region_slug,
                listing_page_number=page_number,
                listing_url=listing_url,
            )

        if isinstance(error, ScraperResponseError):
            return ScraperResponseError(
                message=error.message,
                request_url=error.request_url,
                status_code=error.status_code,
                region_slug=self._region_slug,
                listing_page_number=page_number,
                listing_url=listing_url,
            )

        return ScraperHttpError(
            message=error.message,
            request_url=error.request_url,
            region_slug=self._region_slug,
            listing_page_number=page_number,
            listing_url=listing_url,
        )

    def _build_raw_listing_record(
        self,
        estate_url: str,
        listing_id: str,
        page_number: int,
        raw_payload: dict[str, JsonValue],
        detail_html: str,
    ) -> RawListingRecord:
        """Create the canonical scraper-owned raw listing contract."""

        return RawListingRecord(
            listing_id=listing_id,
            source_url=estate_url,
            captured_at_utc=datetime.now(timezone.utc),
            source_payload=raw_payload,
            source_metadata=RawSourceMetadata(
                region=self._region_slug,
                listing_page_number=page_number,
                scrape_run_id=self._scrape_run_id,
                http_status=DETAIL_PAGE_HTTP_STATUS,
                parser_version=DETAIL_PAGE_PARSER_VERSION,
                captured_from=DETAIL_PAGE_CAPTURED_FROM,
            ),
            raw_page_snapshot=detail_html if self._capture_raw_page_snapshots else None,
        )

    def _persist_markup_failure_artifact(
        self,
        estate_url: str,
        page_number: int,
        detail_html: str,
        failure_message: str,
    ) -> None:
        """Persist raw detail HTML for one listing skipped after markup validation."""

        if self._markup_failure_artifact_handler is None:
            return

        self._markup_failure_artifact_handler(
            DetailMarkupFailureArtifact(
                listing_id=self._extract_listing_id(estate_url),
                source_url=estate_url,
                captured_at_utc=datetime.now(timezone.utc),
                raw_page_snapshot=detail_html,
                failure_message=failure_message,
                source_metadata=RawSourceMetadata(
                    region=self._region_slug,
                    listing_page_number=page_number,
                    scrape_run_id=self._scrape_run_id,
                    http_status=DETAIL_PAGE_HTTP_STATUS,
                    parser_version=DETAIL_PAGE_PARSER_VERSION,
                    captured_from=DETAIL_PAGE_CAPTURED_FROM,
                ),
            ),
        )

    @staticmethod
    def _extract_listing_id(estate_url: str) -> str:
        """Extract the source listing identifier from the detail page URL."""

        return estate_url.rstrip("/").split("/")[-1]

    def _build_markup_response_error(
        self,
        error: ScraperMarkupError,
        request_url: str,
        page_number: int,
        listing_url: str | None,
    ) -> ScraperResponseError:
        """Convert parser validation failures into contextual response errors."""

        return ScraperResponseError(
            message=error.message,
            request_url=request_url,
            status_code=DETAIL_PAGE_HTTP_STATUS,
            region_slug=self._region_slug,
            listing_page_number=page_number,
            listing_url=listing_url,
        )
