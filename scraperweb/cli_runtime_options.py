"""Runtime option schema and validation for scraper CLI commands."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Sequence


DEFAULT_MAX_ESTATES = 50
DEFAULT_OUTPUT_DIR = Path("data/raw")
ALL_CZECHIA_REGION = "all-czechia"

REGION_CHOICES = (
    ALL_CZECHIA_REGION,
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


class RuntimeCliOptionsError(ValueError):
    """Raised when scraper CLI options are internally inconsistent."""


@dataclass(frozen=True)
class RuntimeCliOptions:
    """Runtime options accepted by the scraper command-line interface."""

    regions: tuple[str, ...]
    max_pages: int | None
    max_estates: int
    fail_on_http_error: bool
    verbose: bool
    quiet: bool
    storage_backend: StorageBackend
    mongodb_uri: str | None
    mongodb_database: str | None
    output_dir: Path | None


def build_runtime_cli_options(
    *,
    regions: Sequence[str] | None = None,
    max_pages: int | None = None,
    max_estates: int = DEFAULT_MAX_ESTATES,
    fail_on_http_error: bool = False,
    verbose: bool = False,
    quiet: bool = False,
    storage_backend: StorageBackend = StorageBackend.FILESYSTEM,
    mongodb_uri: str | None = None,
    mongodb_database: str | None = None,
    output_dir: Path | None = DEFAULT_OUTPUT_DIR,
) -> RuntimeCliOptions:
    """Build validated runtime CLI options for scraper execution."""

    validated_regions = _normalize_regions(regions)
    _validate_positive_limit("max_pages", max_pages)
    _validate_positive_limit("max_estates", max_estates)
    _validate_output_mode(verbose=verbose, quiet=quiet)
    _validate_backend_specific_options(
        storage_backend=storage_backend,
        mongodb_uri=mongodb_uri,
        mongodb_database=mongodb_database,
        output_dir=output_dir,
    )
    return RuntimeCliOptions(
        regions=validated_regions,
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


def _normalize_regions(regions: Sequence[str] | None) -> tuple[str, ...]:
    """Normalize region selection while preserving declaration order."""

    if not regions:
        return (ALL_CZECHIA_REGION,)

    unique_regions = tuple(dict.fromkeys(regions))
    invalid_regions = [region for region in unique_regions if region not in REGION_CHOICES]
    if invalid_regions:
        raise RuntimeCliOptionsError(
            "Unsupported region value(s): "
            f"{', '.join(invalid_regions)}. Supported values: {', '.join(REGION_CHOICES)}.",
        )
    return unique_regions


def _validate_positive_limit(name: str, value: int | None) -> None:
    """Validate that an optional numeric runtime limit is greater than zero."""

    if value is not None and value <= 0:
        raise RuntimeCliOptionsError(f"{name} must be greater than zero.")


def _validate_backend_specific_options(
    *,
    storage_backend: StorageBackend,
    mongodb_uri: str | None,
    mongodb_database: str | None,
    output_dir: Path | None,
) -> None:
    """Validate mutually exclusive backend option groups."""

    using_mongodb_options = mongodb_uri is not None or mongodb_database is not None

    if storage_backend == StorageBackend.MONGODB:
        if output_dir not in (None, DEFAULT_OUTPUT_DIR):
            raise RuntimeCliOptionsError(
                "--output-dir is not allowed with --storage-backend mongodb.",
            )
        return

    if using_mongodb_options:
        raise RuntimeCliOptionsError(
            "--mongodb-uri and --mongodb-database are only allowed "
            "with --storage-backend mongodb.",
        )

    if output_dir is None:
        raise RuntimeCliOptionsError(
            "--output-dir must be set when --storage-backend filesystem is used.",
        )


def _validate_output_mode(*, verbose: bool, quiet: bool) -> None:
    """Reject mutually exclusive terminal output modes."""

    if verbose and quiet:
        raise RuntimeCliOptionsError("--verbose and --quiet cannot be used together.")
