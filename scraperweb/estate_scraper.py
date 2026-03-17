"""Scraper runtime composed from explicit clients, parsers, and storage adapters."""

from __future__ import annotations

from typing import Final

import requests as req
from loguru import logger

from scraperweb.application.acquisition_service import RawAcquisitionService
from scraperweb.cli_runtime_options import REGION_CHOICES, RuntimeCliOptions, StorageBackend
from scraperweb.config import get_settings
from scraperweb.persistence.repositories import (
    FilesystemRawRecordRepository,
    MongoRawRecordRepository,
    RawRecordRepository,
)
from scraperweb.scraping.clients import DetailPageClient, ListingPageClient, SrealityHttpClient
from scraperweb.scraping.parsers import SrealityDetailPageParser, SrealityListingPageParser

LINKS_CZ: Final[list[str]] = [
    "https://www.sreality.cz/hledani/prodej/byty/praha?strana=",
    "https://www.sreality.cz/hledani/prodej/byty/stredocesky-kraj?strana=",
    "https://www.sreality.cz/hledani/prodej/byty/jihocesky-kraj?strana=",
    "https://www.sreality.cz/hledani/prodej/byty/plzensky-kraj?strana=",
    "https://www.sreality.cz/hledani/prodej/byty/karlovarsky-kraj?strana=",
    "https://www.sreality.cz/hledani/prodej/byty/ustecky-kraj?strana=",
    "https://www.sreality.cz/hledani/prodej/byty/liberecky-kraj?strana=",
    "https://www.sreality.cz/hledani/prodej/byty/kralovehradecky-kraj?strana=",
    "https://www.sreality.cz/hledani/prodej/byty/pardubicky-kraj?strana=",
    "https://www.sreality.cz/hledani/prodej/byty/vysocina-kraj?strana=",
    "https://www.sreality.cz/hledani/prodej/byty/jihomoravsky-kraj?strana=",
    "https://www.sreality.cz/hledani/prodej/byty/zlinsky-kraj?strana=",
    "https://www.sreality.cz/hledani/prodej/byty/olomoucky-kraj?strana=",
    "https://www.sreality.cz/hledani/prodej/byty/moravskoslezsky-kraj?strana=",
]


def build_raw_record_repository(options: RuntimeCliOptions) -> RawRecordRepository:
    """Build the configured raw record repository for the selected storage backend."""

    settings = get_settings()
    if options.storage_backend == StorageBackend.MONGODB:
        return MongoRawRecordRepository(
            mongodb_uri=options.mongodb_uri or settings.mongodb_uri,
            mongodb_database=options.mongodb_database or settings.mongodb_database,
        )

    output_dir = options.output_dir
    if output_dir is None:
        raise ValueError("Filesystem backend requires an output directory.")
    return FilesystemRawRecordRepository(output_dir=output_dir)


def _resolve_region_indices(regions: tuple[str, ...]) -> list[int]:
    """Resolve selected region slugs to district indices used by current runtime."""

    region_index_by_slug = {slug: index for index, slug in enumerate(REGION_CHOICES)}
    return [region_index_by_slug[slug] for slug in regions]


def run_scraper(options: RuntimeCliOptions) -> int:
    """Run the scraper with runtime limits and region selection from CLI options."""

    tracked_estates = 0
    http_client = SrealityHttpClient(http_module=req)
    raw_record_repository = build_raw_record_repository(options)

    for district_index in _resolve_region_indices(options.regions):
        region_slug = REGION_CHOICES[district_index]
        acquisition_service = RawAcquisitionService(
            listing_page_client=ListingPageClient(http_client),
            detail_page_client=DetailPageClient(http_client),
            listing_page_parser=SrealityListingPageParser(),
            detail_page_parser=SrealityDetailPageParser(),
            raw_record_repository=raw_record_repository,
            region_slug=region_slug,
            capture_raw_page_snapshots=False,
        )
        district_link = LINKS_CZ[district_index]
        tracked_estates = acquisition_service.collect_for_region(
            district_link=district_link,
            max_pages=options.max_pages,
            max_estates=options.max_estates,
            tracked_estates=tracked_estates,
        )
        logger.debug("Tracked estates after region {}: {}", region_slug, tracked_estates)

        if tracked_estates >= options.max_estates:
            logger.info("Reached max estate limit: {}.", options.max_estates)
            logger.info("Processed {} estates.", tracked_estates)
            return tracked_estates

    logger.info("Processed {} estates.", tracked_estates)
    return tracked_estates


def main() -> None:
    """Run the scraper CLI entrypoint."""

    from scraperweb.cli import main as cli_main

    cli_main()
