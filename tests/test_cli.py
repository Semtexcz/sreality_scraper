"""Tests for the Typer-based command-line interface."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from scraperweb.cli import app
from scraperweb.cli_runtime_options import StorageBackend


runner = CliRunner()


def test_scrape_command_runs_with_explicit_runtime_options(monkeypatch) -> None:
    """Pass validated runtime options from the CLI into the scraper runtime."""

    captured_options = {}

    def fake_run_scraper(options) -> int:
        captured_options["value"] = options
        return 7

    monkeypatch.setattr("scraperweb.cli.run_scraper", fake_run_scraper)

    result = runner.invoke(
        app,
        [
            "scrape",
            "--region",
            "praha",
            "--region",
            "jihomoravsky-kraj",
            "--max-pages",
            "3",
            "--max-estates",
            "12",
            "--storage-backend",
            "filesystem",
            "--output-dir",
            "tmp/raw",
        ],
    )

    assert result.exit_code == 0
    assert "Processed 7 estates." in result.stdout
    assert captured_options["value"].regions == ("praha", "jihomoravsky-kraj")
    assert captured_options["value"].max_pages == 3
    assert captured_options["value"].max_estates == 12
    assert captured_options["value"].storage_backend == StorageBackend.FILESYSTEM
    assert captured_options["value"].output_dir == Path("tmp/raw")


def test_scrape_command_rejects_mongodb_options_for_filesystem_backend() -> None:
    """Show a CLI validation error for invalid backend-specific options."""

    result = runner.invoke(
        app,
        [
            "scrape",
            "--storage-backend",
            "filesystem",
            "--mongodb-uri",
            "mongodb://example.test:27017",
        ],
    )

    assert result.exit_code != 0
    assert "--mongodb-uri and --mongodb-database are only allowed" in result.stdout


def test_scrape_command_rejects_unknown_region() -> None:
    """Show a CLI validation error for unsupported region values."""

    result = runner.invoke(
        app,
        [
            "scrape",
            "--region",
            "not-a-region",
        ],
    )

    assert result.exit_code != 0
    assert "Unsupported region value(s): not-a-region." in result.stdout


def test_load_towns_command_runs_loader(monkeypatch) -> None:
    """Delegate the towns subcommand directly to the loader service."""

    called = {"value": False}

    def fake_load_towns() -> None:
        called["value"] = True

    monkeypatch.setattr("scraperweb.cli.load_towns", fake_load_towns)

    result = runner.invoke(app, ["load-towns"])

    assert result.exit_code == 0
    assert called["value"] is True


def test_load_districts_command_reports_inserted_rows(monkeypatch) -> None:
    """Delegate the districts subcommand and report the inserted row count."""

    monkeypatch.setattr("scraperweb.cli.load_districts", lambda: 15)

    result = runner.invoke(app, ["load-districts"])

    assert result.exit_code == 0
    assert "Inserted 15 district rows." in result.stdout
