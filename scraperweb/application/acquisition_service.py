"""Application service orchestrating listing discovery and raw detail persistence."""

from __future__ import annotations

from uuid import uuid4

from loguru import logger

from scraperweb.persistence.repositories import RawRecordRepository
from scraperweb.scraper.clients import DetailPageClient, ListingPageClient
from scraperweb.scraper.exceptions import ScraperHttpError
from scraperweb.scraper.parsers import SrealityDetailPageParser, SrealityListingPageParser
from scraperweb.scraper.runtime import RawListingCollector


class RawAcquisitionService:
    """Coordinate listing-page traversal and raw detail record persistence."""

    def __init__(
        self,
        listing_page_client: ListingPageClient,
        detail_page_client: DetailPageClient,
        listing_page_parser: SrealityListingPageParser,
        detail_page_parser: SrealityDetailPageParser,
        raw_record_repository: RawRecordRepository,
        region_slug: str,
        scrape_run_id: str | None = None,
        capture_raw_page_snapshots: bool = False,
        fail_on_http_error: bool = False,
    ) -> None:
        """Store injected collaborators used by the acquisition workflow."""

        self._fail_on_http_error = fail_on_http_error
        self._raw_record_repository = raw_record_repository
        self._raw_listing_collector = RawListingCollector(
            listing_page_client=listing_page_client,
            detail_page_client=detail_page_client,
            listing_page_parser=listing_page_parser,
            detail_page_parser=detail_page_parser,
            region_slug=region_slug,
            scrape_run_id=scrape_run_id or str(uuid4()),
            capture_raw_page_snapshots=capture_raw_page_snapshots,
            fail_on_detail_http_error=fail_on_http_error,
        )

    def collect_for_region(
        self,
        district_link: str,
        max_pages: int | None,
        max_estates: int,
        tracked_estates: int,
    ) -> int:
        """Collect detail records for one region until limits are reached."""

        try:
            for record in self._raw_listing_collector.collect_region_records(
                district_link=district_link,
                max_pages=max_pages,
            ):
                self._raw_record_repository.save_record(record)

                tracked_estates += 1
                if tracked_estates >= max_estates:
                    return tracked_estates
        except ScraperHttpError as error:
            logger.error(
                "Scraper HTTP failure for region={} page={} listing_url={} request_url={}: {}",
                error.region_slug,
                error.listing_page_number,
                error.listing_url,
                error.request_url,
                error.message,
            )
            if self._fail_on_http_error:
                raise

        return tracked_estates
