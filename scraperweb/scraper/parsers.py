"""HTML parsers owned by the scraper stage."""

from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup as bSoup


def remove_spaces(value: str) -> str:
    """Remove all whitespace from the provided string."""

    return re.sub(r"\s+", "", value)


def clean_string(value: str) -> str:
    """Remove zero-width and non-breaking spaces from the provided string."""

    return re.sub(r"[\u200b\xa0]", "", value)


class SrealityListingPageParser:
    """Parser for listing pagination and detail links."""

    def parse_range_of_estates(self, listing_html: str) -> int:
        """Infer page count as ``max(strana) + 1`` from listing HTML."""

        received_data = bSoup(listing_html, "html.parser")
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
        estates: list[str] = []
        for estate in received_data.find_all("a"):
            href = estate.get("href")
            if href and "detail" in href:
                estates.append(f"https://www.sreality.cz{href}")
        return estates


class SrealityDetailPageParser:
    """Parser for estate detail pages."""

    def parse_raw_payload(self, detail_html: str) -> dict[str, Any]:
        """Extract title and ``dt/dd`` values from a detail page."""

        received_data = bSoup(detail_html, "html.parser")
        dictionary_data: dict[str, Any] = {}
        title = received_data.find("h1")
        dictionary_data["Název"] = clean_string(title.text) if title else ""

        dt_elements = received_data.find_all("dt")
        dd_elements = received_data.find_all("dd")

        for dt, dd in zip(dt_elements, dd_elements):
            term = dt.get_text(strip=True)
            description = dd.get_text(strip=True)
            sub_items = [div.get_text(strip=True) for div in dd.find_all("div")]
            if sub_items:
                description = ", ".join(sub_items)
            dictionary_data[term] = clean_string(description)

        return dictionary_data
