"""Application service orchestrating listing discovery and detail collection."""

from __future__ import annotations

from typing import Any, Callable

from scraperweb.scraping.clients import DetailPageClient, ListingPageClient
from scraperweb.scraping.parsers import SrealityDetailPageParser, SrealityListingPageParser


class RawAcquisitionService:
    """Coordinate listing-page traversal and detail payload collection."""

    def __init__(
        self,
        listing_page_client: ListingPageClient,
        detail_page_client: DetailPageClient,
        listing_page_parser: SrealityListingPageParser,
        detail_page_parser: SrealityDetailPageParser,
        on_record_collected: Callable[[int, str, dict[str, Any]], None],
    ) -> None:
        """Store injected collaborators used by the acquisition workflow."""

        self._listing_page_client = listing_page_client
        self._detail_page_client = detail_page_client
        self._listing_page_parser = listing_page_parser
        self._detail_page_parser = detail_page_parser
        self._on_record_collected = on_record_collected

    def collect_for_region(
        self,
        district_index: int,
        district_link: str,
        max_pages: int,
        max_estates: int,
        tracked_estates: int,
    ) -> int:
        """Collect detail records for one region until limits are reached."""

        first_page_html = self._listing_page_client.fetch(f"{district_link}1")
        listing_range = self._listing_page_parser.parse_range_of_estates(first_page_html)
        page_limit = min(listing_range, max_pages)

        for page_number in range(1, page_limit + 1):
            listing_html = self._listing_page_client.fetch(f"{district_link}{page_number}")
            estate_urls = self._listing_page_parser.parse_estate_urls(listing_html)

            for estate_url in estate_urls:
                detail_html = self._detail_page_client.fetch(estate_url)
                raw_payload = self._detail_page_parser.parse_raw_payload(detail_html)
                self._on_record_collected(district_index, estate_url, raw_payload)

                tracked_estates += 1
                if tracked_estates >= max_estates:
                    return tracked_estates

        return tracked_estates
