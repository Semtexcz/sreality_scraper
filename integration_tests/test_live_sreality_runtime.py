"""Live integration tests for the Sreality scraper runtime."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
import requests

from scraperweb.application.acquisition_service import RawAcquisitionService
from scraperweb.persistence.repositories import FilesystemRawRecordRepository
from scraperweb.scraping.clients import DetailPageClient, ListingPageClient, SrealityHttpClient
from scraperweb.scraping.parsers import SrealityDetailPageParser, SrealityListingPageParser

LIVE_PRAGUE_LISTING_URL = "https://www.sreality.cz/hledani/prodej/byty/praha?strana="
LIVE_TEST_ENV_VAR = "RUN_LIVE_INTEGRATION_TESTS"


def _live_tests_enabled() -> bool:
    """Return whether the opt-in live integration suite should run."""

    return os.getenv(LIVE_TEST_ENV_VAR, "").strip() == "1"


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not _live_tests_enabled(),
        reason=(
            "Live integration tests are disabled by default. "
            f"Set {LIVE_TEST_ENV_VAR}=1 to enable them."
        ),
    ),
]


def _load_single_stored_record(output_dir: Path) -> dict[str, object]:
    """Load the single JSON record produced by the live runtime test."""

    json_paths = sorted(output_dir.rglob("*.json"))
    assert len(json_paths) == 1
    return json.loads(json_paths[0].read_text(encoding="utf-8"))


def test_live_runtime_processes_one_real_estate(tmp_path: Path) -> None:
    """Fetch one real listing from Sreality and persist its raw payload."""

    service = RawAcquisitionService(
        listing_page_client=ListingPageClient(SrealityHttpClient()),
        detail_page_client=DetailPageClient(SrealityHttpClient()),
        listing_page_parser=SrealityListingPageParser(),
        detail_page_parser=SrealityDetailPageParser(),
        raw_record_repository=FilesystemRawRecordRepository(tmp_path),
        region_slug="praha",
        scrape_run_id="live-integration-test",
        capture_raw_page_snapshots=True,
    )

    try:
        tracked_estates = service.collect_for_region(
            district_link=LIVE_PRAGUE_LISTING_URL,
            max_pages=1,
            max_estates=1,
            tracked_estates=0,
        )
    except requests.RequestException as error:
        pytest.skip(f"Live Sreality request failed: {error}")

    assert tracked_estates == 1

    stored_record = _load_single_stored_record(tmp_path)
    assert stored_record["listing_id"]
    assert str(stored_record["source_url"]).startswith("https://www.sreality.cz/detail/")
    assert stored_record["source_metadata"]["region"] == "praha"
    assert stored_record["source_metadata"]["scrape_run_id"] == "live-integration-test"
    assert stored_record["raw_page_snapshot"]
    assert stored_record["source_payload"]["Název"]
