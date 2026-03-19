"""Typer-based command-line interface for scraper operations."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from loguru import logger

from scraperweb.cli_runtime_options import (
    DEFAULT_OUTPUT_DIR,
    REGION_CHOICES,
    RuntimeCliOptions,
    RuntimeCliOptionsError,
    StorageBackend,
    build_runtime_cli_options,
)
from scraperweb.enrichment import EnrichmentWorkflowError, run_filesystem_enrichment_workflow
from scraperweb.estate_scraper import run_scraper
from scraperweb.normalization import NormalizationWorkflowError, run_filesystem_normalization_workflow
from scraperweb.progress import TerminalScrapeProgressReporter


app = typer.Typer(
    help=(
        "Run raw-data acquisition plus filesystem normalization and enrichment workflows."
    ),
    no_args_is_help=True,
    pretty_exceptions_enable=False,
)


@app.callback()
def app_callback() -> None:
    """Expose scraper commands through a stable top-level CLI group."""


def _build_scrape_options(
    *,
    regions: list[str] | None,
    max_pages: int | None,
    max_estates: int | None,
    resume_existing: bool,
    fail_on_http_error: bool,
    verbose: bool,
    quiet: bool,
    storage_backend: StorageBackend,
    mongodb_uri: str | None,
    mongodb_database: str | None,
    output_dir: Path,
) -> RuntimeCliOptions:
    """Build validated scraper runtime options from Typer command arguments."""

    try:
        return build_runtime_cli_options(
            regions=regions,
            max_pages=max_pages,
            max_estates=max_estates,
            resume_existing=resume_existing,
            fail_on_http_error=fail_on_http_error,
            verbose=verbose,
            quiet=quiet,
            storage_backend=storage_backend,
            mongodb_uri=mongodb_uri,
            mongodb_database=mongodb_database,
            output_dir=output_dir,
        )
    except RuntimeCliOptionsError as error:
        raise typer.BadParameter(str(error)) from error


@app.command("scrape")
def scrape_command(
    region: Annotated[
        list[str] | None,
        typer.Option(
            "--region",
            help=(
                "Region slug to scrape. Repeat the option to target multiple regions. "
                "When omitted, the global all-czechia listing target is scraped."
            ),
            show_default=False,
        ),
    ] = None,
    max_pages: Annotated[
        int | None,
        typer.Option(
            "--max-pages",
            min=1,
            help="Optional maximum number of listing pages per selected region.",
        ),
    ] = None,
    max_estates: Annotated[
        int | None,
        typer.Option(
            "--max-estates",
            min=1,
            help=(
                "Optional maximum number of raw estate records processed in one run. "
                "When omitted, scraping continues until pagination is exhausted."
            ),
        ),
    ] = None,
    resume_existing: Annotated[
        bool,
        typer.Option(
            "--resume-existing",
            help=(
                "Skip detail-page downloads for listings that already have a "
                "persisted raw record in the selected backend and region."
            ),
        ),
    ] = False,
    fail_on_http_error: Annotated[
        bool,
        typer.Option(
            "--fail-on-http-error/--skip-http-errors",
            help=(
                "Fail fast on scraper HTTP errors instead of logging the failure "
                "and continuing when possible."
            ),
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            help="Show detailed progress output for pages and processed listings.",
        ),
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            help="Suppress progress output and show only the final summary and errors.",
        ),
    ] = False,
    storage_backend: Annotated[
        StorageBackend,
        typer.Option(
            "--storage-backend",
            case_sensitive=False,
            help="Storage backend used to persist raw scraper outputs.",
        ),
    ] = StorageBackend.FILESYSTEM,
    mongodb_uri: Annotated[
        str | None,
        typer.Option(
            "--mongodb-uri",
            help="MongoDB connection URI. Allowed only with --storage-backend mongodb.",
        ),
    ] = None,
    mongodb_database: Annotated[
        str | None,
        typer.Option(
            "--mongodb-database",
            help="MongoDB database name. Allowed only with --storage-backend mongodb.",
        ),
    ] = None,
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output-dir",
            help="Filesystem output directory for raw scraper artifacts.",
        ),
    ] = DEFAULT_OUTPUT_DIR,
) -> None:
    """Scrape raw listing records from `sreality.cz` into the selected backend."""

    options = _build_scrape_options(
        regions=region,
        max_pages=max_pages,
        max_estates=max_estates,
        resume_existing=resume_existing,
        fail_on_http_error=fail_on_http_error,
        verbose=verbose,
        quiet=quiet,
        storage_backend=storage_backend,
        mongodb_uri=mongodb_uri,
        mongodb_database=mongodb_database,
        output_dir=output_dir,
    )
    logger.info(
        "Selected runtime options: regions={}, max_pages={}, max_estates={}, resume_existing={}, fail_on_http_error={}, verbose={}, quiet={}, storage_backend={}",
        options.regions,
        options.max_pages,
        options.max_estates,
        options.resume_existing,
        options.fail_on_http_error,
        options.verbose,
        options.quiet,
        options.storage_backend.value,
    )
    processed_estates = run_scraper(
        options,
        progress_reporter=TerminalScrapeProgressReporter(
            output=typer.echo,
            verbose=options.verbose,
            quiet=options.quiet,
        ),
    )
    typer.echo(f"Processed {processed_estates} estates.")


@app.command("normalize")
def normalize_command(
    region: Annotated[
        str | None,
        typer.Option(
            "--region",
            help="Normalize every raw snapshot stored under one region directory.",
            show_default=False,
        ),
    ] = None,
    listing_id: Annotated[
        str | None,
        typer.Option(
            "--listing-id",
            help="Normalize every stored raw snapshot for one listing id.",
            show_default=False,
        ),
    ] = None,
    scrape_run_id: Annotated[
        str | None,
        typer.Option(
            "--scrape-run-id",
            help="Normalize every stored raw snapshot captured in one scrape run.",
            show_default=False,
        ),
    ] = None,
    input_dir: Annotated[
        Path,
        typer.Option(
            "--input-dir",
            help="Filesystem input directory that contains persisted raw snapshots.",
        ),
    ] = DEFAULT_OUTPUT_DIR,
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output-dir",
            help="Filesystem output directory for normalized JSON artifacts.",
        ),
    ] = Path("data/normalized"),
) -> None:
    """Normalize persisted raw filesystem snapshots into stable JSON artifacts."""

    try:
        normalized_records = run_filesystem_normalization_workflow(
            input_dir=input_dir,
            output_dir=output_dir,
            region=region,
            listing_id=listing_id,
            scrape_run_id=scrape_run_id,
        )
    except NormalizationWorkflowError as error:
        raise typer.BadParameter(str(error)) from error

    typer.echo(f"Normalized {normalized_records} records.")


@app.command("enrich")
def enrich_command(
    region: Annotated[
        str | None,
        typer.Option(
            "--region",
            help="Enrich every normalized snapshot stored under one region directory.",
            show_default=False,
        ),
    ] = None,
    listing_id: Annotated[
        str | None,
        typer.Option(
            "--listing-id",
            help="Enrich every stored normalized snapshot for one listing id.",
            show_default=False,
        ),
    ] = None,
    scrape_run_id: Annotated[
        str | None,
        typer.Option(
            "--scrape-run-id",
            help="Enrich every stored normalized snapshot captured in one scrape run.",
            show_default=False,
        ),
    ] = None,
    input_dir: Annotated[
        Path,
        typer.Option(
            "--input-dir",
            help="Filesystem input directory that contains persisted normalized snapshots.",
        ),
    ] = Path("data/normalized"),
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output-dir",
            help="Filesystem output directory for enriched JSON artifacts.",
        ),
    ] = Path("data/enriched"),
) -> None:
    """Enrich persisted normalized filesystem snapshots into stable JSON artifacts."""

    try:
        enriched_records = run_filesystem_enrichment_workflow(
            input_dir=input_dir,
            output_dir=output_dir,
            region=region,
            listing_id=listing_id,
            scrape_run_id=scrape_run_id,
        )
    except EnrichmentWorkflowError as error:
        raise typer.BadParameter(str(error)) from error

    typer.echo(f"Enriched {enriched_records} records.")


def main() -> None:
    """Run the top-level Typer application."""

    app()


__all__ = [
    "REGION_CHOICES",
    "app",
    "enrich_command",
    "main",
    "normalize_command",
    "scrape_command",
]
