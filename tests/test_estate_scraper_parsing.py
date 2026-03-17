"""Deterministic parser tests for estate scraper helper functions."""

from __future__ import annotations

from scraperweb import estate_scraper


def test_remove_spaces_removes_all_whitespace() -> None:
    """Verify that all whitespace characters are removed from input."""

    assert estate_scraper.remove_spaces(" 1 250 000 \n Kč\t") == "1250000Kč"


def test_clean_string_removes_non_printing_spaces() -> None:
    """Verify that zero-width and non-breaking spaces are removed."""

    assert estate_scraper.clean_string("Byt\u200b\xa03+kk") == "Byt3+kk"


def test_get_range_of_estates_returns_max_page_plus_one(monkeypatch, response_factory) -> None:
    """Parse available pages from HTML anchors and return ``max + 1``."""

    html = """
    <html>
      <body>
        <a href="/hledani/prodej/byty/praha?strana=1">1</a>
        <a href="/hledani/prodej/byty/praha?strana=6">6</a>
        <a href="/hledani/prodej/byty/praha?strana=x">x</a>
      </body>
    </html>
    """
    monkeypatch.setattr(estate_scraper.req, "get", lambda _url, timeout: response_factory(html))

    assert estate_scraper.get_range_of_estates("https://example.test") == 7


def test_get_list_of_estates_returns_absolute_detail_links(monkeypatch, response_factory) -> None:
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
    monkeypatch.setattr(estate_scraper.req, "get", lambda _url, timeout: response_factory(html))

    assert estate_scraper.get_list_of_estates("https://example.test/listing") == [
        "https://www.sreality.cz/detail/prodej/byt/123",
        "https://www.sreality.cz/detail/prodej/byt/456",
    ]


def test_get_final_data_for_estate_to_database_extracts_title_and_pairs(monkeypatch, response_factory) -> None:
    """Build parsed estate dictionary from title and dt/dd pairs."""

    html = """
    <html>
      <body>
        <h1>Byt\u200b\xa03+kk 75 m², Brno</h1>
        <dl>
          <dt>Celková cena:</dt>
          <dd>7 500 000 Kč</dd>
          <dt>Stavba:</dt>
          <dd><div>Cihla</div><div>Velmi dobrý</div></dd>
        </dl>
      </body>
    </html>
    """
    monkeypatch.setattr(estate_scraper.req, "get", lambda _url, timeout: response_factory(html))

    assert estate_scraper.get_final_data_for_estate_to_database("https://example.test/estate") == {
        "Název": "Byt3+kk 75 m², Brno",
        "Celková cena:": "7 500 000 Kč",
        "Stavba:": "Cihla, Velmi dobrý",
    }
