"""Runtime option schema and validation for scraper CLI commands."""

from __future__ import annotations

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


class RuntimeCliOptionsError(ValueError):
    """Raised when scraper CLI options are internally inconsistent."""


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


def build_runtime_cli_options(
    *,
    regions: Sequence[str] | None = None,
    max_pages: int = DEFAULT_MAX_PAGES,
    max_estates: int = DEFAULT_MAX_ESTATES,
    storage_backend: StorageBackend = StorageBackend.FILESYSTEM,
    mongodb_uri: str | None = None,
    mongodb_database: str | None = None,
    output_dir: Path | None = DEFAULT_OUTPUT_DIR,
) -> RuntimeCliOptions:
    """Build validated runtime CLI options for scraper execution."""

    validated_regions = _normalize_regions(regions)
    _validate_positive_limit("max_pages", max_pages)
    _validate_positive_limit("max_estates", max_estates)
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
        storage_backend=storage_backend,
        mongodb_uri=mongodb_uri,
        mongodb_database=mongodb_database,
        output_dir=output_dir,
    )


def _normalize_regions(regions: Sequence[str] | None) -> tuple[str, ...]:
    """Normalize region selection while preserving declaration order."""

    if not regions:
        return REGION_CHOICES

    unique_regions = tuple(dict.fromkeys(regions))
    invalid_regions = [region for region in unique_regions if region not in REGION_CHOICES]
    if invalid_regions:
        raise RuntimeCliOptionsError(
            "Unsupported region value(s): "
            f"{', '.join(invalid_regions)}. Supported values: {', '.join(REGION_CHOICES)}.",
        )
    return unique_regions


def _validate_positive_limit(name: str, value: int) -> None:
    """Validate that a numeric runtime limit is greater than zero."""

    if value <= 0:
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
