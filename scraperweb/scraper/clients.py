"""HTTP clients owned by the scraper stage."""

from __future__ import annotations

from typing import Any

import requests as req

from scraperweb.scraper.exceptions import ScraperResponseError, ScraperTransportError


DEFAULT_REQUEST_TIMEOUT_SECONDS = 30
DEFAULT_MAX_HTTP_ATTEMPTS = 3


class SrealityHttpClient:
    """Minimal HTTP client wrapper used by scraper page clients."""

    def __init__(
        self,
        http_module: Any | None = None,
        timeout_seconds: int = DEFAULT_REQUEST_TIMEOUT_SECONDS,
        max_attempts: int = DEFAULT_MAX_HTTP_ATTEMPTS,
    ) -> None:
        """Initialize the client with an injectable HTTP module."""

        self._http_module = http_module or req
        self._timeout_seconds = timeout_seconds
        self._max_attempts = max_attempts

    def get_text(self, url: str, timeout: int | None = None) -> str:
        """Download URL content with bounded retries for transient failures."""

        request_timeout = timeout or self._timeout_seconds

        for attempt in range(1, self._max_attempts + 1):
            try:
                response = self._http_module.get(url, timeout=request_timeout)
            except (req.exceptions.Timeout, req.exceptions.ConnectionError) as error:
                if attempt == self._max_attempts:
                    raise ScraperTransportError(
                        message=(
                            "HTTP transport failure after bounded retries for "
                            f"{url!r}: {error}"
                        ),
                        request_url=url,
                        timeout_seconds=request_timeout,
                        attempts=attempt,
                    ) from error
                continue
            except req.exceptions.RequestException as error:
                raise ScraperResponseError(
                    message=f"HTTP request failure for {url!r}: {error}",
                    request_url=url,
                ) from error

            self._raise_for_invalid_response(url=url, response=response)
            return response.text

        raise AssertionError("HTTP retry loop exhausted without returning or raising.")

    @staticmethod
    def _raise_for_invalid_response(url: str, response: Any) -> None:
        """Validate response status and content before scraper parsing begins."""

        status_code = getattr(response, "status_code", None)
        if status_code is None or not 200 <= status_code < 300:
            raise ScraperResponseError(
                message=f"Received non-success HTTP status for {url!r}: {status_code}",
                request_url=url,
                status_code=status_code,
            )

        response_text = getattr(response, "text", None)
        if response_text is None or not response_text.strip():
            raise ScraperResponseError(
                message=f"Received empty HTTP response content for {url!r}.",
                request_url=url,
                status_code=status_code,
            )


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
