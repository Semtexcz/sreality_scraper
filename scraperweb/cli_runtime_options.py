"""Runtime option schema and validation for scraper CLI entrypoints."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Sequence


DEFAULT_MAX_PAGES = 1
DEFAULT_MAX_ESTATES = 50
DEFAULT_OUTPUT_DIR = Path("data/raw")

REGION_CHOICES = (
    "praha",
    "stredocesky-kraj",
    "jihocesky-kraj",
    "plzensky-kraj",
    "karlovarsky-kraj",
    "ustecky-kraj",
    "liberecky-kraj",
    "kralovehradecky-kraj",
    "pardubicky-kraj",
    "vysocina-kraj",
    "jihomoravsky-kraj",
    "zlinsky-kraj",
    "olomoucky-kraj",
    "moravskoslezsky-kraj",
)


class StorageBackend(StrEnum):
    """Supported storage backends for scraper runtime output."""

    MONGODB = "mongodb"
    FILESYSTEM = "filesystem"


@dataclass(frozen=True)
class RuntimeCliOptions:
    """Runtime options accepted by the scraper command-line interface."""

    regions: tuple[str, ...]
    max_pages: int
    max_estates: int
    storage_backend: StorageBackend
    mongodb_uri: str | None
    mongodb_database: str | None
    output_dir: Path | None


def positive_int(value: str) -> int:
    """Parse and validate a positive integer for CLI options."""

    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    """Build the runtime options parser for current and future CLI frontends."""

    parser = argparse.ArgumentParser(
        prog="scraperweb",
        description=(
            "Run scraper with explicit runtime controls suitable for future Typer "
            "migration."
        ),
    )
    parser.add_argument(
        "--region",
        dest="regions",
        action="append",
        choices=REGION_CHOICES,
        default=[],
        help=(
            "Region slug to scrape. Repeat the option to target multiple regions. "
            "When omitted, all regions are scraped."
        ),
    )
    parser.add_argument(
        "--max-pages",
        dest="max_pages",
        type=positive_int,
        default=DEFAULT_MAX_PAGES,
        help=(
            "Maximum number of listing pages per selected region. "
            f"Default: {DEFAULT_MAX_PAGES}."
        ),
    )
    parser.add_argument(
        "--max-estates",
        dest="max_estates",
        type=positive_int,
        default=DEFAULT_MAX_ESTATES,
        help=(
            "Maximum number of estates processed in a run. "
            f"Default: {DEFAULT_MAX_ESTATES}."
        ),
    )
    parser.add_argument(
        "--storage-backend",
        dest="storage_backend",
        choices=[backend.value for backend in StorageBackend],
        default=StorageBackend.FILESYSTEM.value,
        help="Storage backend for raw data output.",
    )
    parser.add_argument(
        "--mongodb-uri",
        dest="mongodb_uri",
        default=None,
        help="MongoDB connection URI. Allowed only with --storage-backend mongodb.",
    )
    parser.add_argument(
        "--mongodb-database",
        dest="mongodb_database",
        default=None,
        help="MongoDB database name. Allowed only with --storage-backend mongodb.",
    )
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for filesystem backend.",
    )
    return parser


def parse_runtime_cli_options(argv: Sequence[str] | None = None) -> RuntimeCliOptions:
    """Parse and validate CLI runtime options."""

    parser = build_parser()
    args = parser.parse_args(argv)
    storage_backend = StorageBackend(args.storage_backend)
    _validate_backend_specific_options(
        parser=parser,
        storage_backend=storage_backend,
        mongodb_uri=args.mongodb_uri,
        mongodb_database=args.mongodb_database,
        output_dir=args.output_dir,
    )

    regions = tuple(dict.fromkeys(args.regions)) if args.regions else REGION_CHOICES
    return RuntimeCliOptions(
        regions=regions,
        max_pages=args.max_pages,
        max_estates=args.max_estates,
        storage_backend=storage_backend,
        mongodb_uri=args.mongodb_uri,
        mongodb_database=args.mongodb_database,
        output_dir=args.output_dir,
    )


def _validate_backend_specific_options(
    parser: argparse.ArgumentParser,
    storage_backend: StorageBackend,
    mongodb_uri: str | None,
    mongodb_database: str | None,
    output_dir: Path | None,
) -> None:
    """Validate mutually exclusive backend option groups."""

    using_mongodb_options = mongodb_uri is not None or mongodb_database is not None
    using_output_dir = output_dir is not None

    if storage_backend == StorageBackend.MONGODB:
        if output_dir != DEFAULT_OUTPUT_DIR and output_dir is not None:
            parser.error("--output-dir is not allowed with --storage-backend mongodb")
        return

    if using_mongodb_options:
        parser.error(
            "--mongodb-uri and --mongodb-database are only allowed "
            "with --storage-backend mongodb",
        )

    if not using_output_dir:
        parser.error(
            "--output-dir must be set when --storage-backend filesystem is used",
        )
