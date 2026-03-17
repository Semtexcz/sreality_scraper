# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and the project uses Semantic Versioning.

## [0.1.5] - 2026-03-17

### Added

- added bootstrap `tests/` coverage for configuration defaults and deterministic parsing helpers
- added shared test fixtures for mocked HTTP responses to keep tests independent from live network services

### Changed

- configured pytest discovery via `pyproject.toml` and registered `pytest` as a Poetry development dependency

### Fixed

- fixed `scraperweb.config.Settings` so environment variable overrides are evaluated at runtime instead of module import time

## [0.1.4] - 2026-03-17

### Changed

- rewrote backlog tasks into a structured front-matter format with problem statements and definitions of done
- documented the new task template in `project/README.md`

## [0.1.3] - 2026-03-17

### Added

- added backlog tasks for the raw-data refactor, storage abstraction, Typer CLI, and refactored test coverage

### Changed

- updated the roadmap to reflect the new implementation sequence for the raw-data-only project goal

## [0.1.2] - 2026-03-17

### Changed

- clarified the project scope in the documentation as raw data acquisition from `sreality.cz`
- documented that scraper outputs should remain unprocessed and unnormalized
- recorded the open storage decision between MongoDB and filesystem-based persistence

## [0.1.1] - 2026-03-17

### Added

- added top-level project governance and contributor rules in `AGENTS.md`
- added technical documentation in `docs/` for architecture, modules, artifacts, and roadmap
- added lightweight task tracking in `project/` with backlog and done records
- added Poetry script entrypoints for scraper, town loader, and district loader
- added centralized runtime configuration in `scraperweb.config`
- added dedicated runtime modules for estate scraping, town loading, and district loading
- added root `README.md` and `.gitignore`

### Changed

- reorganized repository layout to separate source code, scripts, datasets, docs, and project tracking
- moved CSV reference datasets from `scraperweb/` to `data/`
- converted legacy script-style modules into compatibility wrappers around refactored implementations
- replaced hard-coded runtime values with environment-based configuration defaults

### Removed

- removed tracked Python bytecode artifacts from the repository
- removed generated API HTML files from the active working tree snapshot pending regeneration
