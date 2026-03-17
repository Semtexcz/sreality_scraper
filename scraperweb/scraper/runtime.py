"""Scraper-stage runtime services that emit raw listing contracts."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import datetime, timezone
from itertools import count

from loguru import logger

from scraperweb.progress import ScrapeProgressReporter
from scraperweb.scraper.clients import DetailPageClient, ListingPageClient
from scraperweb.scraper.exceptions import (
    ScraperHttpError,
    ScraperMarkupError,
    ScraperResponseError,
    ScraperTransportError,
)
from scraperweb.scraper.models import JsonValue, RawListingRecord, RawSourceMetadata
from scraperweb.scraper.parsers import SrealityDetailPageParser, SrealityListingPageParser

DETAIL_PAGE_PARSER_VERSION = "sreality-detail-v1"
DETAIL_PAGE_HTTP_STATUS = 200
DETAIL_PAGE_CAPTURED_FROM = "detail_page"


@dataclass
class ListingTraversalState:
    """Track observed listing-page outcomes during one region traversal."""

    seen_page_signatures: set[tuple[str, ...]] = field(default_factory=set)
    seen_estate_urls: set[str] = field(default_factory=set)


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

    def collect_region_records(
        self,
        district_link: str,
        max_pages: int | None,
    ) -> Iterator[RawListingRecord]:
        """Yield raw listing records for one region until traversal exhaustion."""

        traversal_state = ListingTraversalState()
        page_numbers = range(1, max_pages + 1) if max_pages is not None else count(1)

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

            should_continue, new_estate_urls = self._evaluate_listing_page(
                estate_urls=estate_urls,
                traversal_state=traversal_state,
            )
            if not should_continue:
                return
            self._progress_reporter.listing_page_completed(
                region_slug=self._region_slug,
                page_number=page_number,
                discovered_estates=len(new_estate_urls),
            )

            for estate_url in new_estate_urls:
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
                    raise self._build_markup_response_error(
                        error=error,
                        request_url=estate_url,
                        page_number=page_number,
                        listing_url=estate_url,
                    ) from error
                yield self._build_raw_listing_record(
                    estate_url=estate_url,
                    page_number=page_number,
                    raw_payload=raw_payload,
                    detail_html=detail_html,
                )

    def _evaluate_listing_page(
        self,
        estate_urls: list[str],
        traversal_state: ListingTraversalState,
    ) -> tuple[bool, list[str]]:
        """Return whether traversal should continue and which estate URLs are new."""

        if not estate_urls:
            return False, []

        page_signature = tuple(estate_urls)
        if page_signature in traversal_state.seen_page_signatures:
            return False, []

        traversal_state.seen_page_signatures.add(page_signature)
        new_estate_urls = [
            estate_url
            for estate_url in estate_urls
            if estate_url not in traversal_state.seen_estate_urls
        ]
        if not new_estate_urls:
            return False, []

        traversal_state.seen_estate_urls.update(new_estate_urls)
        return True, new_estate_urls

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
        page_number: int,
        raw_payload: dict[str, JsonValue],
        detail_html: str,
    ) -> RawListingRecord:
        """Create the canonical scraper-owned raw listing contract."""

        return RawListingRecord(
            listing_id=self._extract_listing_id(estate_url),
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
