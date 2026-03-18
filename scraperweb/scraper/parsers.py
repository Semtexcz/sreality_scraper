"""HTML parsers owned by the scraper stage.

The scraper keeps extraction intentionally raw, but it still validates the
minimum structural anchors that define the raw contract. Listing pages must
contain at least one detail link. Detail pages must contain a non-empty title
and at least one aligned ``dt/dd`` attribute pair.
"""

from __future__ import annotations

import re

from bs4 import BeautifulSoup as bSoup

from scraperweb.scraper.exceptions import ScraperMarkupError
from scraperweb.scraper.models import JsonValue


def remove_spaces(value: str) -> str:
    """Remove all whitespace from the provided string."""

    return re.sub(r"\s+", "", value)


def clean_string(value: str) -> str:
    """Remove zero-width and non-breaking spaces from the provided string."""

    return re.sub(r"[\u200b\xa0]", "", value)


def extract_dd_description(description_element: bSoup) -> str:
    """Return a normalized ``dd`` description while ignoring empty sub-items."""

    sub_items = [
        cleaned_item
        for div in description_element.find_all("div")
        if (cleaned_item := clean_string(div.get_text(strip=True)))
    ]
    if sub_items:
        return ", ".join(sub_items)
    return clean_string(description_element.get_text(strip=True))


class SrealityListingPageParser:
    """Parser for listing pagination hints and detail links."""

    def parse_range_of_estates(self, listing_html: str) -> int:
        """Return a best-effort pagination hint derived from ``strana`` anchors."""

        received_data = bSoup(listing_html, "html.parser")
        self._extract_estate_urls(received_data)
        page_numbers: list[int] = []
        for estate in received_data.find_all("a"):
            href = estate.get("href")
            if href and "strana" in href and "=" in href:
                try:
                    page_numbers.append(int(href.split("=")[1]))
                except ValueError:
                    continue
        return (max(page_numbers) if page_numbers else 1) + 1

    def parse_estate_urls(self, listing_html: str) -> list[str]:
        """Extract absolute detail-page URLs from listing HTML."""

        received_data = bSoup(listing_html, "html.parser")
        return self._extract_estate_urls(received_data)

    def _extract_estate_urls(self, listing_document: bSoup) -> list[str]:
        """Return unique detail URLs or raise when listing anchors are missing."""

        estates: list[str] = []
        for estate in listing_document.find_all("a"):
            href = estate.get("href")
            if href and href.startswith("/detail/"):
                estates.append(f"https://www.sreality.cz{href}")

        unique_estates = list(dict.fromkeys(estates))
        if not unique_estates:
            raise ScraperMarkupError(
                "listing page validation failed: expected at least one detail link",
            )
        return unique_estates


class SrealityDetailPageParser:
    """Parser for estate detail pages."""

    def parse_raw_payload(self, detail_html: str) -> dict[str, JsonValue]:
        """Extract title and ``dt/dd`` values from a validated detail page."""

        received_data = bSoup(detail_html, "html.parser")
        dictionary_data: dict[str, JsonValue] = {}
        title = received_data.find("h1")
        if title is None:
            raise ScraperMarkupError(
                "detail page validation failed: missing non-empty listing title",
            )

        title_text = clean_string(title.get_text(strip=True))
        if not title_text:
            raise ScraperMarkupError(
                "detail page validation failed: missing non-empty listing title",
            )
        dictionary_data["Název"] = title_text

        dt_elements = received_data.find_all("dt")
        dd_elements = received_data.find_all("dd")
        if not dt_elements or not dd_elements:
            raise ScraperMarkupError(
                "detail page validation failed: expected at least one dt/dd attribute pair",
            )
        if len(dt_elements) != len(dd_elements):
            raise ScraperMarkupError(
                "detail page validation failed: dt/dd attribute counts do not match",
            )

        for dt, dd in zip(dt_elements, dd_elements):
            term = dt.get_text(strip=True)
            cleaned_description = extract_dd_description(dd)
            if not term:
                raise ScraperMarkupError(
                    "detail page validation failed: encountered empty attribute name or value",
                )
            if not cleaned_description:
                continue
            dictionary_data[term] = cleaned_description

        return dictionary_data
