"""Tests for the Typer-based command-line interface."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from scraperweb.cli import app
from scraperweb.cli_runtime_options import StorageBackend
from scraperweb.enrichment import EnrichmentWorkflowError
from scraperweb.normalization import NormalizationWorkflowError


runner = CliRunner()


def test_root_help_lists_scrape_normalize_and_enrich_commands() -> None:
    """Expose raw acquisition plus replay workflows on the public CLI surface."""

    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "scrape" in result.stdout
    assert "normalize" in result.stdout
    assert "enrich" in result.stdout
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


def test_normalize_command_runs_with_region_scope(monkeypatch) -> None:
    """Pass region-scoped normalization arguments into the workflow runner."""

    captured_arguments = {}

    def fake_run_filesystem_normalization_workflow(**kwargs) -> int:
        """Capture normalization workflow arguments passed from the CLI."""

        captured_arguments.update(kwargs)
        return 4

    monkeypatch.setattr(
        "scraperweb.cli.run_filesystem_normalization_workflow",
        fake_run_filesystem_normalization_workflow,
    )

    result = runner.invoke(
        app,
        [
            "normalize",
            "--region",
            "all-czechia",
            "--input-dir",
            "tmp/raw",
            "--output-dir",
            "tmp/normalized",
        ],
    )

    assert result.exit_code == 0
    assert "Normalized 4 records." in result.stdout
    assert captured_arguments == {
        "input_dir": Path("tmp/raw"),
        "output_dir": Path("tmp/normalized"),
        "region": "all-czechia",
        "listing_id": None,
        "scrape_run_id": None,
    }


def test_normalize_command_supports_listing_scope(monkeypatch) -> None:
    """Pass listing-scoped normalization arguments into the workflow runner."""

    captured_arguments = {}

    def fake_run_filesystem_normalization_workflow(**kwargs) -> int:
        """Capture normalization workflow arguments passed from the CLI."""

        captured_arguments.update(kwargs)
        return 2

    monkeypatch.setattr(
        "scraperweb.cli.run_filesystem_normalization_workflow",
        fake_run_filesystem_normalization_workflow,
    )

    result = runner.invoke(
        app,
        [
            "normalize",
            "--listing-id",
            "2664846156",
        ],
    )

    assert result.exit_code == 0
    assert "Normalized 2 records." in result.stdout
    assert captured_arguments["listing_id"] == "2664846156"
    assert captured_arguments["region"] is None
    assert captured_arguments["scrape_run_id"] is None
    assert captured_arguments["input_dir"] == Path("data/raw")
    assert captured_arguments["output_dir"] == Path("data/normalized")


def test_normalize_command_reports_workflow_validation_errors(monkeypatch) -> None:
    """Translate workflow validation failures into CLI parameter errors."""

    def fake_run_filesystem_normalization_workflow(**kwargs) -> int:
        """Raise a workflow validation error for CLI coverage."""

        del kwargs
        raise NormalizationWorkflowError(
            "Exactly one normalization selector must be provided.",
        )

    monkeypatch.setattr(
        "scraperweb.cli.run_filesystem_normalization_workflow",
        fake_run_filesystem_normalization_workflow,
    )

    result = runner.invoke(app, ["normalize"])

    assert result.exit_code != 0
    assert "Exactly one normalization selector must be provided." in result.stdout


def test_enrich_command_runs_with_scrape_run_scope(monkeypatch) -> None:
    """Pass scrape-run-scoped enrichment arguments into the workflow runner."""

    captured_arguments = {}

    def fake_run_filesystem_enrichment_workflow(**kwargs) -> int:
        """Capture enrichment workflow arguments passed from the CLI."""

        captured_arguments.update(kwargs)
        return 5

    monkeypatch.setattr(
        "scraperweb.cli.run_filesystem_enrichment_workflow",
        fake_run_filesystem_enrichment_workflow,
    )

    result = runner.invoke(
        app,
        [
            "enrich",
            "--scrape-run-id",
            "dc733c67-1091-4a08-831f-f8243eb1b8f6",
            "--input-dir",
            "tmp/normalized",
            "--output-dir",
            "tmp/enriched",
        ],
    )

    assert result.exit_code == 0
    assert "Enriched 5 records." in result.stdout
    assert captured_arguments == {
        "input_dir": Path("tmp/normalized"),
        "output_dir": Path("tmp/enriched"),
        "region": None,
        "listing_id": None,
        "scrape_run_id": "dc733c67-1091-4a08-831f-f8243eb1b8f6",
    }


def test_enrich_command_supports_listing_scope(monkeypatch) -> None:
    """Pass listing-scoped enrichment arguments into the workflow runner."""

    captured_arguments = {}

    def fake_run_filesystem_enrichment_workflow(**kwargs) -> int:
        """Capture enrichment workflow arguments passed from the CLI."""

        captured_arguments.update(kwargs)
        return 2

    monkeypatch.setattr(
        "scraperweb.cli.run_filesystem_enrichment_workflow",
        fake_run_filesystem_enrichment_workflow,
    )

    result = runner.invoke(
        app,
        [
            "enrich",
            "--listing-id",
            "2664846156",
        ],
    )

    assert result.exit_code == 0
    assert "Enriched 2 records." in result.stdout
    assert captured_arguments["listing_id"] == "2664846156"
    assert captured_arguments["region"] is None
    assert captured_arguments["scrape_run_id"] is None
    assert captured_arguments["input_dir"] == Path("data/normalized")
    assert captured_arguments["output_dir"] == Path("data/enriched")


def test_enrich_command_reports_workflow_validation_errors(monkeypatch) -> None:
    """Translate workflow validation failures into CLI parameter errors."""

    def fake_run_filesystem_enrichment_workflow(**kwargs) -> int:
        """Raise a workflow validation error for CLI coverage."""

        del kwargs
        raise EnrichmentWorkflowError(
            "Exactly one enrichment selector must be provided.",
        )

    monkeypatch.setattr(
        "scraperweb.cli.run_filesystem_enrichment_workflow",
        fake_run_filesystem_enrichment_workflow,
    )

    result = runner.invoke(app, ["enrich"])

    assert result.exit_code != 0
    assert "Exactly one enrichment selector must be provided." in result.stdout
