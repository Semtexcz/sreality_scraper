"""Tests for CLI runtime option parsing and validation rules."""

from __future__ import annotations

from pathlib import Path

import pytest

from scraperweb.cli_runtime_options import (
    DEFAULT_MAX_ESTATES,
    DEFAULT_MAX_PAGES,
    DEFAULT_OUTPUT_DIR,
    REGION_CHOICES,
    StorageBackend,
    parse_runtime_cli_options,
)


def test_parse_runtime_cli_options_uses_safe_defaults() -> None:
    """Use explicit development-safe defaults when no CLI options are provided."""

    options = parse_runtime_cli_options([])

    assert options.regions == REGION_CHOICES
    assert options.max_pages == DEFAULT_MAX_PAGES
    assert options.max_estates == DEFAULT_MAX_ESTATES
    assert options.storage_backend == StorageBackend.FILESYSTEM
    assert options.mongodb_uri is None
    assert options.mongodb_database is None
    assert options.output_dir == DEFAULT_OUTPUT_DIR


def test_parse_runtime_cli_options_supports_region_and_limits() -> None:
    """Parse selected regions and explicit limit overrides."""

    options = parse_runtime_cli_options(
        [
            "--region",
            "praha",
            "--region",
            "jihomoravsky-kraj",
            "--max-pages",
            "3",
            "--max-estates",
            "120",
        ],
    )

    assert options.regions == ("praha", "jihomoravsky-kraj")
    assert options.max_pages == 3
    assert options.max_estates == 120


def test_parse_runtime_cli_options_rejects_non_positive_limits() -> None:
    """Fail parsing when numeric runtime limits are not positive."""

    with pytest.raises(SystemExit):
        parse_runtime_cli_options(["--max-pages", "0"])

    with pytest.raises(SystemExit):
        parse_runtime_cli_options(["--max-estates", "-1"])


def test_parse_runtime_cli_options_accepts_mongodb_backend_with_mongo_options() -> None:
    """Allow MongoDB-specific options when MongoDB backend is selected."""

    options = parse_runtime_cli_options(
        [
            "--storage-backend",
            "mongodb",
            "--mongodb-uri",
            "mongodb://example.test:27017",
            "--mongodb-database",
            "RawListings",
        ],
    )

    assert options.storage_backend == StorageBackend.MONGODB
    assert options.mongodb_uri == "mongodb://example.test:27017"
    assert options.mongodb_database == "RawListings"
    assert options.output_dir == DEFAULT_OUTPUT_DIR


def test_parse_runtime_cli_options_rejects_mongodb_options_for_filesystem_backend() -> None:
    """Reject MongoDB-specific options when filesystem backend is selected."""

    with pytest.raises(SystemExit):
        parse_runtime_cli_options(
            [
                "--storage-backend",
                "filesystem",
                "--mongodb-uri",
                "mongodb://example.test:27017",
            ],
        )


def test_parse_runtime_cli_options_rejects_output_dir_for_mongodb_backend() -> None:
    """Reject filesystem output options when MongoDB backend is selected."""

    with pytest.raises(SystemExit):
        parse_runtime_cli_options(
            [
                "--storage-backend",
                "mongodb",
                "--output-dir",
                "tmp/raw",
            ],
        )


def test_parse_runtime_cli_options_accepts_custom_output_dir_for_filesystem_backend() -> None:
    """Allow custom output directory when filesystem backend is selected."""

    options = parse_runtime_cli_options(
        [
            "--storage-backend",
            "filesystem",
            "--output-dir",
            "tmp/raw",
        ],
    )

    assert options.output_dir == Path("tmp/raw")
