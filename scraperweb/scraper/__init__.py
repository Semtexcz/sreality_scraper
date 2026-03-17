"""Canonical scraper-stage package for raw acquisition contracts and adapters."""

from scraperweb.scraper.clients import DetailPageClient, ListingPageClient, SrealityHttpClient
from scraperweb.scraper.exceptions import (
    ScraperHttpError,
    ScraperResponseError,
    ScraperTransportError,
)
from scraperweb.scraper.models import RawListingRecord, RawSourceMetadata
from scraperweb.scraper.parsers import (
    SrealityDetailPageParser,
    SrealityListingPageParser,
    clean_string,
    remove_spaces,
)
from scraperweb.scraper.runtime import RawListingCollector

__all__ = [
    "DetailPageClient",
    "ListingPageClient",
    "RawListingCollector",
    "RawListingRecord",
    "RawSourceMetadata",
    "ScraperHttpError",
    "ScraperResponseError",
    "ScraperTransportError",
    "SrealityDetailPageParser",
    "SrealityHttpClient",
    "SrealityListingPageParser",
    "clean_string",
    "remove_spaces",
]
