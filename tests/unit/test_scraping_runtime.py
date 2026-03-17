"""Regression tests for scraping clients and representative parser fixtures."""

from __future__ import annotations

from typing import Any, Callable

from scraperweb.scraper.clients import (
    DetailPageClient,
    ListingPageClient,
    SrealityHttpClient,
)
from scraperweb.scraper.parsers import SrealityDetailPageParser, SrealityListingPageParser


class FakeHttpModule:
    """Minimal HTTP module stub that records requests and returns configured text."""

    def __init__(self, response_text: str) -> None:
        """Store deterministic response text and initialize captured calls."""

        self._response_text = response_text
        self.calls: list[tuple[str, int]] = []

    def get(self, url: str, timeout: int) -> Any:
        """Record request arguments and return a response-like object."""

        self.calls.append((url, timeout))
        return type("Response", (), {"text": self._response_text})()


class RecordingHttpClient:
    """Minimal HTTP client stub for page-client delegation tests."""

    def __init__(self) -> None:
        """Initialize recorded URL storage."""

        self.urls: list[str] = []

    def get_text(self, url: str, timeout: int = 30) -> str:
        """Record the requested URL and return deterministic content."""

        self.urls.append(url)
        return f"html:{url}:{timeout}"


def test_sreality_http_client_returns_response_text_and_forwards_timeout() -> None:
    """Return response text while forwarding URL and timeout to the HTTP module."""

    http_module = FakeHttpModule("<html>payload</html>")
    client = SrealityHttpClient(http_module=http_module)

    response_text = client.get_text("https://example.test/listing", timeout=12)

    assert response_text == "<html>payload</html>"
    assert http_module.calls == [("https://example.test/listing", 12)]


def test_page_clients_delegate_fetches_to_shared_http_client() -> None:
    """Delegate listing and detail fetches to the shared HTTP client contract."""

    http_client = RecordingHttpClient()
    listing_client = ListingPageClient(http_client=http_client)
    detail_client = DetailPageClient(http_client=http_client)

    listing_html = listing_client.fetch("https://example.test/listing")
    detail_html = detail_client.fetch("https://example.test/detail/123")

    assert listing_html == "html:https://example.test/listing:30"
    assert detail_html == "html:https://example.test/detail/123:30"
    assert http_client.urls == [
        "https://example.test/listing",
        "https://example.test/detail/123",
    ]


def test_listing_parser_reads_representative_fixture(
    html_fixture_loader: Callable[[str], str],
) -> None:
    """Parse pagination and detail links from a representative listing fixture."""

    listing_html = html_fixture_loader("listing_page_sample.html")
    parser = SrealityListingPageParser()

    assert parser.parse_range_of_estates(listing_html) == 5
    assert parser.parse_estate_urls(listing_html) == [
        "https://www.sreality.cz/detail/prodej/byt/praha-nove-mesto/1111111111",
        "https://www.sreality.cz/detail/prodej/byt/praha-karlin/2222222222",
    ]


def test_detail_parser_reads_representative_fixture(
    html_fixture_loader: Callable[[str], str],
) -> None:
    """Parse raw payload fields from a representative detail-page fixture."""

    detail_html = html_fixture_loader("detail_page_sample.html")
    parser = SrealityDetailPageParser()

    assert parser.parse_raw_payload(detail_html) == {
        "Název": "Byt2+kk 58 m², Praha 8 - Karlín",
        "Celková cena:": "8 490 000 Kč",
        "Poznámka k ceně:": "včetně provize",
        "Stavba:": "Cihla, Velmi dobrý",
        "Energetická náročnost:": "B",
    }
