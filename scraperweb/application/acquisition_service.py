"""Application service orchestrating listing discovery and raw detail persistence."""

from __future__ import annotations

from uuid import uuid4

from scraperweb.persistence.repositories import RawRecordRepository
from scraperweb.scraper.clients import DetailPageClient, ListingPageClient
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
    ) -> None:
        """Store injected collaborators used by the acquisition workflow."""

        self._raw_record_repository = raw_record_repository
        self._raw_listing_collector = RawListingCollector(
            listing_page_client=listing_page_client,
            detail_page_client=detail_page_client,
            listing_page_parser=listing_page_parser,
            detail_page_parser=detail_page_parser,
            region_slug=region_slug,
            scrape_run_id=scrape_run_id or str(uuid4()),
            capture_raw_page_snapshots=capture_raw_page_snapshots,
        )

    def collect_for_region(
        self,
        district_link: str,
        max_pages: int,
        max_estates: int,
        tracked_estates: int,
    ) -> int:
        """Collect detail records for one region until limits are reached."""

        for record in self._raw_listing_collector.collect_region_records(
            district_link=district_link,
            max_pages=max_pages,
        ):
            self._raw_record_repository.save_record(record)

            tracked_estates += 1
            if tracked_estates >= max_estates:
                return tracked_estates

        return tracked_estates
