"""Typer-based command-line interface for scraper operations."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from loguru import logger

from scraperweb.cli_runtime_options import (
    DEFAULT_MAX_ESTATES,
    DEFAULT_OUTPUT_DIR,
    REGION_CHOICES,
    RuntimeCliOptions,
    RuntimeCliOptionsError,
    StorageBackend,
    build_runtime_cli_options,
)
from scraperweb.estate_scraper import run_scraper
from scraperweb.progress import TerminalScrapeProgressReporter


app = typer.Typer(
    help=(
        "Run raw-data scraper operations. "
        "The CLI is intentionally scoped to raw acquisition and persistence flows."
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
    max_estates: int,
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
        int,
        typer.Option(
            "--max-estates",
            min=1,
            help="Maximum number of raw estate records processed in one run.",
        ),
    ] = DEFAULT_MAX_ESTATES,
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
        fail_on_http_error=fail_on_http_error,
        verbose=verbose,
        quiet=quiet,
        storage_backend=storage_backend,
        mongodb_uri=mongodb_uri,
        mongodb_database=mongodb_database,
        output_dir=output_dir,
    )
    logger.info(
        "Selected runtime options: regions={}, max_pages={}, max_estates={}, fail_on_http_error={}, verbose={}, quiet={}, storage_backend={}",
        options.regions,
        options.max_pages,
        options.max_estates,
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


def main() -> None:
    """Run the top-level Typer application."""

    app()


__all__ = [
    "REGION_CHOICES",
    "app",
    "main",
    "scrape_command",
]
