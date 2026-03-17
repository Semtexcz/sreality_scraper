"""Transitional compatibility wrapper for scraper-stage HTTP clients."""

from scraperweb.scraper.clients import DetailPageClient, ListingPageClient, SrealityHttpClient

__all__ = [
    "DetailPageClient",
    "ListingPageClient",
    "SrealityHttpClient",
]
