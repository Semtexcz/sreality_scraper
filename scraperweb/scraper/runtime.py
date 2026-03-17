"""Scraper-stage runtime services that emit raw listing contracts."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone

from scraperweb.scraper.clients import DetailPageClient, ListingPageClient
from scraperweb.scraper.models import JsonValue, RawListingRecord, RawSourceMetadata
from scraperweb.scraper.parsers import SrealityDetailPageParser, SrealityListingPageParser

DETAIL_PAGE_PARSER_VERSION = "sreality-detail-v1"
DETAIL_PAGE_HTTP_STATUS = 200
DETAIL_PAGE_CAPTURED_FROM = "detail_page"


class RawListingCollector:
    """Collect raw listing records from listing and detail page HTML."""

    def __init__(
        self,
        listing_page_client: ListingPageClient,
        detail_page_client: DetailPageClient,
        listing_page_parser: SrealityListingPageParser,
        detail_page_parser: SrealityDetailPageParser,
        region_slug: str,
        scrape_run_id: str,
        capture_raw_page_snapshots: bool = False,
    ) -> None:
        """Store collaborators used to build scraper-owned raw contracts."""

        self._listing_page_client = listing_page_client
        self._detail_page_client = detail_page_client
        self._listing_page_parser = listing_page_parser
        self._detail_page_parser = detail_page_parser
        self._region_slug = region_slug
        self._scrape_run_id = scrape_run_id
        self._capture_raw_page_snapshots = capture_raw_page_snapshots

    def collect_region_records(
        self,
        district_link: str,
        max_pages: int,
    ) -> Iterator[RawListingRecord]:
        """Yield raw listing records for one region up to the requested page limit."""

        first_page_html = self._listing_page_client.fetch(f"{district_link}1")
        listing_range = self._listing_page_parser.parse_range_of_estates(first_page_html)
        page_limit = min(listing_range, max_pages)

        for page_number in range(1, page_limit + 1):
            listing_html = self._listing_page_client.fetch(f"{district_link}{page_number}")
            estate_urls = self._listing_page_parser.parse_estate_urls(listing_html)

            for estate_url in estate_urls:
                detail_html = self._detail_page_client.fetch(estate_url)
                raw_payload = self._detail_page_parser.parse_raw_payload(detail_html)
                yield self._build_raw_listing_record(
                    estate_url=estate_url,
                    page_number=page_number,
                    raw_payload=raw_payload,
                    detail_html=detail_html,
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
