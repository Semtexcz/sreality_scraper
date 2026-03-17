"""HTTP clients owned by the scraper stage."""

from __future__ import annotations

from typing import Any

import requests as req


class SrealityHttpClient:
    """Minimal HTTP client wrapper used by scraper page clients."""

    def __init__(self, http_module: Any | None = None) -> None:
        """Initialize the client with an injectable HTTP module."""

        self._http_module = http_module or req

    def get_text(self, url: str, timeout: int = 30) -> str:
        """Download URL content and return response text."""

        response = self._http_module.get(url, timeout=timeout)
        return response.text


class ListingPageClient:
    """Client responsible for listing-page downloads."""

    def __init__(self, http_client: SrealityHttpClient) -> None:
        """Store injected HTTP client dependency."""

        self._http_client = http_client

    def fetch(self, listing_url: str) -> str:
        """Fetch one listing page HTML document."""

        return self._http_client.get_text(listing_url)


class DetailPageClient:
    """Client responsible for detail-page downloads."""

    def __init__(self, http_client: SrealityHttpClient) -> None:
        """Store injected HTTP client dependency."""

        self._http_client = http_client

    def fetch(self, detail_url: str) -> str:
        """Fetch one detail page HTML document."""

        return self._http_client.get_text(detail_url)
