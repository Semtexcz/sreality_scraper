"""HTTP client abstractions for listing and detail page retrieval."""

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

    def post_json(self, url: str, payload: dict[str, Any], timeout: int = 30) -> None:
        """Send JSON payload to the destination URL."""

        self._http_module.post(url, json=payload, timeout=timeout)


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
