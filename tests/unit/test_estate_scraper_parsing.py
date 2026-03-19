"""Deterministic parser tests for scraper parsing components."""

from __future__ import annotations

import pytest

from scraperweb.scraper.exceptions import ScraperMarkupError
from scraperweb.scraper.parsers import (
    SrealityDetailPageParser,
    SrealityListingPageParser,
    clean_string,
    remove_spaces,
)


def test_remove_spaces_removes_all_whitespace() -> None:
    """Verify that all whitespace characters are removed from input values."""

    assert remove_spaces(" 1 250 000 \n Kč\t") == "1250000Kč"


def test_clean_string_removes_non_printing_spaces() -> None:
    """Verify that zero-width and non-breaking spaces are removed from text."""

    assert clean_string("Byt\u200b\xa03+kk") == "Byt3+kk"


def test_parse_range_of_estates_returns_max_page_plus_one() -> None:
    """Parse available pages from HTML anchors and return ``max + 1``."""

    html = """
    <html>
      <body>
        <a href="/hledani/prodej/byty/praha?strana=1">1</a>
        <a href="/hledani/prodej/byty/praha?strana=6">6</a>
        <a href="/hledani/prodej/byty/praha?strana=x">x</a>
        <a href="/detail/prodej/byt/praha/123">Detail 123</a>
      </body>
    </html>
    """
    parser = SrealityListingPageParser()

    assert parser.parse_range_of_estates(html) == 7


def test_parse_estate_urls_returns_absolute_detail_links() -> None:
    """Extract only detail links and normalize them to absolute URLs."""

    html = """
    <html>
      <body>
        <a href="/detail/prodej/byt/123">Detail 123</a>
        <a href="/detail/prodej/byt/456">Detail 456</a>
        <a href="/hledani/prodej/byty/praha">Search</a>
      </body>
    </html>
    """
    parser = SrealityListingPageParser()

    assert parser.parse_estate_urls(html) == [
        "https://www.sreality.cz/detail/prodej/byt/123",
        "https://www.sreality.cz/detail/prodej/byt/456",
    ]


def test_parse_raw_payload_extracts_title_and_pairs() -> None:
    """Build parsed estate dictionary from title and dt/dd pairs."""

    html = """
    <html>
      <body>
        <h1>Byt\u200b\xa03+kk 75 m², Brno</h1>
        <script>
          window.__INITIAL_STATE__ = {
            "locality": {
              "latitude": 49.1950602,
              "longitude": 16.6068371,
              "inaccuracyType": "gps"
            }
          };
        </script>
        <dl>
          <dt>Celková cena:</dt>
          <dd>7 500 000 Kč</dd>
          <dt>Stavba:</dt>
          <dd><div>Cihla</div><div>Velmi dobrý</div></dd>
        </dl>
      </body>
    </html>
    """
    parser = SrealityDetailPageParser()

    assert parser.parse_raw_payload(html) == {
        "Název": "Byt3+kk 75 m², Brno",
        "Celková cena:": "7 500 000 Kč",
        "Stavba:": "Cihla, Velmi dobrý",
        "source_coordinates": {
            "latitude": 49.1950602,
            "longitude": 16.6068371,
            "source": "detail_locality_payload",
            "precision": "listing",
        },
    }


def test_parse_raw_payload_ignores_empty_div_children_when_value_exists() -> None:
    """Keep non-empty ``dd`` values when decorative child divs are empty."""

    html = """
    <html>
      <body>
        <h1>Byt 2+kk 45 m², Plzeň</h1>
        <dl>
          <dt>Ostatní:</dt>
          <dd><div></div><div>Sklep</div><div>Parkování</div></dd>
        </dl>
      </body>
    </html>
    """
    parser = SrealityDetailPageParser()

    assert parser.parse_raw_payload(html) == {
        "Název": "Byt 2+kk 45 m², Plzeň",
        "Ostatní:": "Sklep, Parkování",
    }


def test_parse_raw_payload_skips_empty_attribute_values() -> None:
    """Skip optional rows whose ``dd`` content is present in markup but empty."""

    html = """
    <html>
      <body>
        <h1>Byt 2+kk 45 m², Plzeň</h1>
        <dl>
          <dt>Ostatní:</dt>
          <dd><div></div></dd>
          <dt>Historie:</dt>
          <dd><div>Rok kolaudace 1945</div></dd>
        </dl>
      </body>
    </html>
    """
    parser = SrealityDetailPageParser()

    assert parser.parse_raw_payload(html) == {
        "Název": "Byt 2+kk 45 m², Plzeň",
        "Historie:": "Rok kolaudace 1945",
    }


def test_parse_raw_payload_rejects_empty_attribute_names() -> None:
    """Reject malformed rows whose ``dt`` label is empty."""

    html = """
    <html>
      <body>
        <h1>Byt 2+kk 45 m², Plzeň</h1>
        <dl>
          <dt></dt>
          <dd>Sklep</dd>
        </dl>
      </body>
    </html>
    """
    parser = SrealityDetailPageParser()

    with pytest.raises(ScraperMarkupError) as exc_info:
        parser.parse_raw_payload(html)

    assert "encountered empty attribute name or value" in exc_info.value.message


def test_parse_raw_payload_omits_source_coordinates_without_complete_locality_pair() -> None:
    """Skip raw source coordinates when the embedded locality payload is incomplete."""

    html = """
    <html>
      <body>
        <h1>Byt 2+kk 45 m², Plzeň</h1>
        <script>
          window.__INITIAL_STATE__ = {
            "locality": {
              "latitude": 49.7384314
            }
          };
        </script>
        <dl>
          <dt>Celková cena:</dt>
          <dd>5 990 000 Kč</dd>
        </dl>
      </body>
    </html>
    """
    parser = SrealityDetailPageParser()

    assert parser.parse_raw_payload(html) == {
        "Název": "Byt 2+kk 45 m², Plzeň",
        "Celková cena:": "5 990 000 Kč",
    }
