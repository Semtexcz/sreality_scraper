# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and the project uses Semantic Versioning.

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
