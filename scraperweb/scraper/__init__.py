"""Canonical scraper-stage package for raw acquisition contracts and adapters."""

from scraperweb.scraper.clients import DetailPageClient, ListingPageClient, SrealityHttpClient
from scraperweb.scraper.models import RawListingRecord, RawSourceMetadata
from scraperweb.scraper.parsers import (
    SrealityDetailPageParser,
    SrealityListingPageParser,
    clean_string,
    remove_spaces,
)

__all__ = [
    "DetailPageClient",
    "ListingPageClient",
    "RawListingRecord",
    "RawSourceMetadata",
    "SrealityDetailPageParser",
    "SrealityHttpClient",
    "SrealityListingPageParser",
    "clean_string",
    "remove_spaces",
]
