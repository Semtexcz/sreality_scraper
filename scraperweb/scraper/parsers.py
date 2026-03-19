"""HTML parsers owned by the scraper stage.

The scraper keeps extraction intentionally raw, but it still validates the
minimum structural anchors that define the raw contract. Listing pages must
contain at least one detail link. Detail pages must contain a non-empty title
and at least one aligned ``dt/dd`` attribute pair.
"""

from __future__ import annotations

import re
import json

from bs4 import BeautifulSoup as bSoup

from scraperweb.scraper.exceptions import ScraperMarkupError
from scraperweb.scraper.models import JsonValue, RawSourceCoordinates


DETAIL_LOCALITY_SOURCE = "detail_locality_payload"
DETAIL_LOCALITY_PRECISION = "listing"
_DETAIL_LOCALITY_PATTERN = re.compile(r'"locality"\s*:\s*\{')


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

        source_coordinates = self.extract_source_coordinates(detail_html)
        if source_coordinates is not None:
            dictionary_data["source_coordinates"] = {
                "latitude": source_coordinates.latitude,
                "longitude": source_coordinates.longitude,
                "source": source_coordinates.source,
                "precision": source_coordinates.precision,
            }

        return dictionary_data

    @classmethod
    def extract_source_coordinates(
        cls,
        detail_html: str,
    ) -> RawSourceCoordinates | None:
        """Extract replay-safe source-backed coordinates from the embedded locality payload."""

        locality_payload = cls._extract_detail_locality_payload(detail_html)
        if locality_payload is None:
            return None

        latitude = cls._parse_json_float(locality_payload.get("latitude"))
        longitude = cls._parse_json_float(locality_payload.get("longitude"))
        if latitude is None or longitude is None:
            return None

        return RawSourceCoordinates(
            latitude=latitude,
            longitude=longitude,
            source=DETAIL_LOCALITY_SOURCE,
            precision=DETAIL_LOCALITY_PRECISION,
        )

    @classmethod
    def _extract_detail_locality_payload(
        cls,
        detail_html: str,
    ) -> dict[str, JsonValue] | None:
        """Return the embedded locality object when it can be parsed from detail HTML."""

        match = _DETAIL_LOCALITY_PATTERN.search(detail_html)
        if match is None:
            return None

        locality_object_text = cls._extract_json_object(
            detail_html,
            object_start_index=match.end() - 1,
        )
        if locality_object_text is None:
            return None

        try:
            payload = json.loads(locality_object_text)
        except json.JSONDecodeError:
            return None

        if not isinstance(payload, dict):
            return None
        return payload

    @staticmethod
    def _extract_json_object(
        value: str,
        *,
        object_start_index: int,
    ) -> str | None:
        """Return one balanced JSON object slice starting at the provided index."""

        depth = 0
        in_string = False
        is_escaped = False

        for index in range(object_start_index, len(value)):
            character = value[index]
            if in_string:
                if is_escaped:
                    is_escaped = False
                elif character == "\\":
                    is_escaped = True
                elif character == '"':
                    in_string = False
                continue

            if character == '"':
                in_string = True
                continue

            if character == "{":
                depth += 1
            elif character == "}":
                depth -= 1
                if depth == 0:
                    return value[object_start_index : index + 1]

        return None

    @staticmethod
    def _parse_json_float(value: JsonValue) -> float | None:
        """Return a float when the JSON value is numeric or a numeric string."""

        if isinstance(value, bool) or value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return None
        return None
