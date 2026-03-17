"""Transitional compatibility wrapper for scraper-stage HTML parsers."""

from scraperweb.scraper.parsers import (
    SrealityDetailPageParser,
    SrealityListingPageParser,
    clean_string,
    remove_spaces,
)

__all__ = [
    "SrealityDetailPageParser",
    "SrealityListingPageParser",
    "clean_string",
    "remove_spaces",
]
