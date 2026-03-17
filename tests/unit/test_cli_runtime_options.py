"""Tests for runtime CLI option normalization and validation rules."""

from __future__ import annotations

from pathlib import Path

import pytest

from scraperweb.cli_runtime_options import (
    ALL_CZECHIA_REGION,
    DEFAULT_MAX_ESTATES,
    DEFAULT_MAX_PAGES,
    DEFAULT_OUTPUT_DIR,
    REGION_CHOICES,
    RuntimeCliOptionsError,
    StorageBackend,
    build_runtime_cli_options,
)


def test_build_runtime_cli_options_uses_safe_defaults() -> None:
    """Use explicit development-safe defaults when no CLI options are provided."""

    options = build_runtime_cli_options()

    assert options.regions == (ALL_CZECHIA_REGION,)
    assert options.max_pages == DEFAULT_MAX_PAGES
    assert options.max_estates == DEFAULT_MAX_ESTATES
    assert options.storage_backend == StorageBackend.FILESYSTEM
    assert options.mongodb_uri is None
    assert options.mongodb_database is None
    assert options.output_dir == DEFAULT_OUTPUT_DIR


def test_build_runtime_cli_options_supports_region_and_limits() -> None:
    """Normalize selected regions and explicit limit overrides."""

    options = build_runtime_cli_options(
        regions=["all-czechia", "jihomoravsky-kraj", "all-czechia"],
        max_pages=3,
        max_estates=120,
    )

    assert options.regions == ("all-czechia", "jihomoravsky-kraj")
    assert options.max_pages == 3
    assert options.max_estates == 120


def test_build_runtime_cli_options_supports_explicit_region_only_runs() -> None:
    """Allow callers to override the global default with specific region slugs."""

    options = build_runtime_cli_options(regions=["praha"])

    assert options.regions == ("praha",)
    assert "praha" in REGION_CHOICES


def test_build_runtime_cli_options_rejects_non_positive_limits() -> None:
    """Reject runtime limits that are not positive integers."""

    with pytest.raises(RuntimeCliOptionsError):
        build_runtime_cli_options(max_pages=0)

    with pytest.raises(RuntimeCliOptionsError):
        build_runtime_cli_options(max_estates=-1)


def test_build_runtime_cli_options_rejects_unknown_regions() -> None:
    """Reject region slugs that are not part of the supported CLI contract."""

    with pytest.raises(RuntimeCliOptionsError):
        build_runtime_cli_options(regions=["unknown-region"])


def test_build_runtime_cli_options_accepts_mongodb_backend_with_mongo_options() -> None:
    """Allow MongoDB-specific options when MongoDB backend is selected."""

    options = build_runtime_cli_options(
        storage_backend=StorageBackend.MONGODB,
        mongodb_uri="mongodb://example.test:27017",
        mongodb_database="RawListings",
    )

    assert options.storage_backend == StorageBackend.MONGODB
    assert options.mongodb_uri == "mongodb://example.test:27017"
    assert options.mongodb_database == "RawListings"
    assert options.output_dir == DEFAULT_OUTPUT_DIR


def test_build_runtime_cli_options_rejects_mongodb_options_for_filesystem_backend() -> None:
    """Reject MongoDB-specific options when filesystem backend is selected."""

    with pytest.raises(RuntimeCliOptionsError):
        build_runtime_cli_options(
            storage_backend=StorageBackend.FILESYSTEM,
            mongodb_uri="mongodb://example.test:27017",
        )


def test_build_runtime_cli_options_rejects_output_dir_for_mongodb_backend() -> None:
    """Reject filesystem output options when MongoDB backend is selected."""

    with pytest.raises(RuntimeCliOptionsError):
        build_runtime_cli_options(
            storage_backend=StorageBackend.MONGODB,
            output_dir=Path("tmp/raw"),
        )


def test_build_runtime_cli_options_accepts_custom_output_dir_for_filesystem_backend() -> None:
    """Allow custom output directory when filesystem backend is selected."""

    options = build_runtime_cli_options(
        storage_backend=StorageBackend.FILESYSTEM,
        output_dir=Path("tmp/raw"),
    )

    assert options.output_dir == Path("tmp/raw")
