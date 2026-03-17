"""Tests for the Typer-based command-line interface."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from scraperweb.cli import app
from scraperweb.cli_runtime_options import StorageBackend


runner = CliRunner()


def test_root_help_lists_only_raw_scrape_command() -> None:
    """Expose only the raw scraper command on the public CLI surface."""

    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "scrape" in result.stdout
    assert "load-towns" not in result.stdout
    assert "load-districts" not in result.stdout


def test_scrape_command_runs_with_explicit_runtime_options(monkeypatch) -> None:
    """Pass validated runtime options from the CLI into the scraper runtime."""

    captured_options = {}

    def fake_run_scraper(options, progress_reporter) -> int:
        captured_options["value"] = options
        del progress_reporter
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
    assert captured_options["value"].fail_on_http_error is False
    assert captured_options["value"].verbose is False
    assert captured_options["value"].quiet is False
    assert captured_options["value"].storage_backend == StorageBackend.FILESYSTEM
    assert captured_options["value"].output_dir == Path("tmp/raw")


def test_scrape_command_defaults_to_global_all_czechia_target(monkeypatch) -> None:
    """Use the global all-Czechia listing target when no region is provided."""

    captured_options = {}

    def fake_run_scraper(options, progress_reporter) -> int:
        """Capture runtime options passed from the CLI."""

        captured_options["value"] = options
        progress_reporter.scrape_started(
            regions=options.regions,
            max_pages=options.max_pages,
            max_estates=options.max_estates,
        )
        return 1

    monkeypatch.setattr("scraperweb.cli.run_scraper", fake_run_scraper)

    result = runner.invoke(app, ["scrape"])

    assert result.exit_code == 0
    assert "Processed 1 estates." in result.stdout
    assert captured_options["value"].regions == ("all-czechia",)
    assert captured_options["value"].max_pages is None
    assert captured_options["value"].fail_on_http_error is False
    assert "Starting scrape:" in result.stdout


def test_scrape_command_supports_fail_fast_http_mode(monkeypatch) -> None:
    """Pass the debug fail-fast HTTP option through to runtime composition."""

    captured_options = {}

    def fake_run_scraper(options, progress_reporter) -> int:
        """Capture runtime options passed from the CLI."""

        captured_options["value"] = options
        del progress_reporter
        return 0

    monkeypatch.setattr("scraperweb.cli.run_scraper", fake_run_scraper)

    result = runner.invoke(app, ["scrape", "--fail-on-http-error"])

    assert result.exit_code == 0
    assert captured_options["value"].fail_on_http_error is True


def test_scrape_command_supports_verbose_progress_mode(monkeypatch) -> None:
    """Pass the verbose progress option through to runtime composition."""

    captured_options = {}

    def fake_run_scraper(options, progress_reporter) -> int:
        """Capture runtime options passed from the CLI."""

        captured_options["value"] = options
        del progress_reporter
        return 0

    monkeypatch.setattr("scraperweb.cli.run_scraper", fake_run_scraper)

    result = runner.invoke(app, ["scrape", "--verbose"])

    assert result.exit_code == 0
    assert captured_options["value"].verbose is True
    assert captured_options["value"].quiet is False


def test_scrape_command_rejects_conflicting_output_modes() -> None:
    """Reject verbose and quiet mode when both are requested."""

    result = runner.invoke(app, ["scrape", "--verbose", "--quiet"])

    assert result.exit_code != 0
    assert "--verbose and --quiet cannot be used together." in result.stdout


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


def test_scrape_command_accepts_mongodb_backend_options(monkeypatch) -> None:
    """Pass MongoDB backend options through CLI validation into the runtime."""

    captured_options = {}

    def fake_run_scraper(options, progress_reporter) -> int:
        """Capture runtime options passed from the CLI."""

        captured_options["value"] = options
        del progress_reporter
        return 2

    monkeypatch.setattr("scraperweb.cli.run_scraper", fake_run_scraper)

    result = runner.invoke(
        app,
        [
            "scrape",
            "--storage-backend",
            "mongodb",
            "--mongodb-uri",
            "mongodb://example.test:27017",
            "--mongodb-database",
            "RawListings",
        ],
    )

    assert result.exit_code == 0
    assert "Processed 2 estates." in result.stdout
    assert captured_options["value"].storage_backend == StorageBackend.MONGODB
    assert captured_options["value"].mongodb_uri == "mongodb://example.test:27017"
    assert captured_options["value"].mongodb_database == "RawListings"
    assert captured_options["value"].output_dir == Path("data/raw")


def test_scrape_command_rejects_non_positive_page_limit() -> None:
    """Reject invalid page limits before the scraper runtime is called."""

    result = runner.invoke(app, ["scrape", "--max-pages", "0"])

    assert result.exit_code != 0
    assert "Invalid value for '--max-pages'" in result.stdout


def test_scrape_command_rejects_non_positive_estate_limit() -> None:
    """Reject invalid estate limits before the scraper runtime is called."""

    result = runner.invoke(app, ["scrape", "--max-estates", "0"])

    assert result.exit_code != 0
    assert "Invalid value for '--max-estates'" in result.stdout
