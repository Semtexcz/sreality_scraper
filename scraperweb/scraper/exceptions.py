"""Scraper-owned HTTP runtime exceptions with explicit failure context."""

from __future__ import annotations


class ScraperHttpError(RuntimeError):
    """Base class for scraper HTTP failures with region and page context."""

    def __init__(
        self,
        message: str,
        request_url: str,
        region_slug: str | None = None,
        listing_page_number: int | None = None,
        listing_url: str | None = None,
    ) -> None:
        """Store failure details used by callers and operator-visible logs."""

        super().__init__(message)
        self.message = message
        self.request_url = request_url
        self.region_slug = region_slug
        self.listing_page_number = listing_page_number
        self.listing_url = listing_url


class ScraperTransportError(ScraperHttpError):
    """Raised when transient transport failures exhaust the bounded retry policy."""

    def __init__(
        self,
        message: str,
        request_url: str,
        timeout_seconds: int,
        attempts: int,
        region_slug: str | None = None,
        listing_page_number: int | None = None,
        listing_url: str | None = None,
    ) -> None:
        """Store transport-specific retry metadata."""

        super().__init__(
            message=message,
            request_url=request_url,
            region_slug=region_slug,
            listing_page_number=listing_page_number,
            listing_url=listing_url,
        )
        self.timeout_seconds = timeout_seconds
        self.attempts = attempts


class ScraperResponseError(ScraperHttpError):
    """Raised when the response is terminally invalid for scraper processing."""

    def __init__(
        self,
        message: str,
        request_url: str,
        status_code: int | None = None,
        region_slug: str | None = None,
        listing_page_number: int | None = None,
        listing_url: str | None = None,
    ) -> None:
        """Store response validation details for terminal runtime failures."""

        super().__init__(
            message=message,
            request_url=request_url,
            region_slug=region_slug,
            listing_page_number=listing_page_number,
            listing_url=listing_url,
        )
        self.status_code = status_code


class ScraperMarkupError(RuntimeError):
    """Raised when page markup no longer satisfies parser-owned invariants."""

    def __init__(self, message: str) -> None:
        """Store a human-readable parser validation failure message."""

        super().__init__(message)
        self.message = message
