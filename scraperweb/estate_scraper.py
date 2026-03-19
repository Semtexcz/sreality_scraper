"""Scraper runtime composed from explicit clients, parsers, and storage adapters."""

from __future__ import annotations

from typing import Final

import requests as req
from loguru import logger

from scraperweb.application.acquisition_service import RawAcquisitionService
from scraperweb.cli_runtime_options import RuntimeCliOptions, StorageBackend
from scraperweb.config import get_settings
from scraperweb.persistence.repositories import (
    FilesystemRawRecordRepository,
    MongoRawRecordRepository,
    RawRecordRepository,
)
from scraperweb.scraper.clients import DetailPageClient, ListingPageClient, SrealityHttpClient
from scraperweb.scraper.parsers import SrealityDetailPageParser, SrealityListingPageParser
from scraperweb.progress import ScrapeProgressReporter

LISTING_URL_BY_REGION: Final[dict[str, str]] = {
    "all-czechia": "https://www.sreality.cz/hledani/prodej/byty?strana=",
    "praha": "https://www.sreality.cz/hledani/prodej/byty/praha?strana=",
    "stredocesky-kraj": "https://www.sreality.cz/hledani/prodej/byty/stredocesky-kraj?strana=",
    "jihocesky-kraj": "https://www.sreality.cz/hledani/prodej/byty/jihocesky-kraj?strana=",
    "plzensky-kraj": "https://www.sreality.cz/hledani/prodej/byty/plzensky-kraj?strana=",
    "karlovarsky-kraj": "https://www.sreality.cz/hledani/prodej/byty/karlovarsky-kraj?strana=",
    "ustecky-kraj": "https://www.sreality.cz/hledani/prodej/byty/ustecky-kraj?strana=",
    "liberecky-kraj": "https://www.sreality.cz/hledani/prodej/byty/liberecky-kraj?strana=",
    "kralovehradecky-kraj": "https://www.sreality.cz/hledani/prodej/byty/kralovehradecky-kraj?strana=",
    "pardubicky-kraj": "https://www.sreality.cz/hledani/prodej/byty/pardubicky-kraj?strana=",
    "vysocina-kraj": "https://www.sreality.cz/hledani/prodej/byty/vysocina-kraj?strana=",
    "jihomoravsky-kraj": "https://www.sreality.cz/hledani/prodej/byty/jihomoravsky-kraj?strana=",
    "zlinsky-kraj": "https://www.sreality.cz/hledani/prodej/byty/zlinsky-kraj?strana=",
    "olomoucky-kraj": "https://www.sreality.cz/hledani/prodej/byty/olomoucky-kraj?strana=",
    "moravskoslezsky-kraj": "https://www.sreality.cz/hledani/prodej/byty/moravskoslezsky-kraj?strana=",
}


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


def run_scraper(
    options: RuntimeCliOptions,
    progress_reporter: ScrapeProgressReporter | None = None,
) -> int:
    """Run the scraper with runtime limits and region selection from CLI options."""

    tracked_estates = 0
    http_client = SrealityHttpClient(http_module=req)
    raw_record_repository = build_raw_record_repository(options)
    reporter = progress_reporter or ScrapeProgressReporter()

    reporter.scrape_started(
        regions=options.regions,
        max_pages=options.max_pages,
        max_estates=options.max_estates,
        resume_existing=options.resume_existing,
    )

    for region_slug in options.regions:
        acquisition_service = RawAcquisitionService(
            listing_page_client=ListingPageClient(http_client),
            detail_page_client=DetailPageClient(http_client),
            listing_page_parser=SrealityListingPageParser(),
            detail_page_parser=SrealityDetailPageParser(),
            raw_record_repository=raw_record_repository,
            region_slug=region_slug,
            resume_existing=options.resume_existing,
            capture_raw_page_snapshots=False,
            fail_on_http_error=options.fail_on_http_error,
            progress_reporter=reporter,
        )
        district_link = LISTING_URL_BY_REGION[region_slug]
        tracked_estates = acquisition_service.collect_for_region(
            district_link=district_link,
            max_pages=options.max_pages,
            max_estates=options.max_estates,
            tracked_estates=tracked_estates,
        )
        logger.debug("Tracked estates after region {}: {}", region_slug, tracked_estates)

        if options.max_estates is not None and tracked_estates >= options.max_estates:
            logger.info("Reached max estate limit: {}.", options.max_estates)
            logger.info("Processed {} estates.", tracked_estates)
            return tracked_estates

    logger.info("Processed {} estates.", tracked_estates)
    return tracked_estates


def main() -> None:
    """Run the scraper CLI entrypoint."""

    from scraperweb.cli import main as cli_main

    cli_main()
