# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and the project uses Semantic Versioning.

## [1.4.0] - 2026-03-17

### Added

- added scraper-owned HTTP exception types that distinguish bounded-retry
  transport failures from terminal response validation errors while preserving
  region, listing-page, and listing-URL context for callers
- added deterministic unit coverage for successful fetches, transient retry
  recovery, retry exhaustion, invalid HTTP status handling, empty-response
  handling, and acquisition-time failure logging

### Changed

- hardened the scraper HTTP client to validate response status and content, apply
  bounded retries only to transient timeout and connection failures, and fail
  fast for terminal request and response errors
- updated raw acquisition flow to log operator-visible failure context before
  propagating scraper-stage HTTP errors without introducing downstream
  normalization or enrichment behavior

## [1.3.3] - 2026-03-17

### Added

- added backlog tasks `TASK-016` through `TASK-018` to break the remaining
  scraper-stage roadmap work into explicit deliverables for HTTP hardening,
  response and markup validation, and traversal stop-condition redesign

## [1.3.2] - 2026-03-17

### Changed

- restructured `docs/ROADMAP.md` from time-based sections into stage-based
  checklists so implemented and remaining work are tracked per pipeline boundary
  and operational area

## [1.3.1] - 2026-03-17

### Changed

- rewrote `docs/ROADMAP.md` to reflect the current implemented repository state,
  distinguish public runtime capabilities from internal stage components, and focus
  future roadmap items on the remaining operational and product gaps

## [1.3.0] - 2026-03-17

### Added

- added a deterministic modeling-stage `EnrichedListingModelingInputBuilder`
  component that accepts `EnrichedListingRecord` inputs only and emits stable
  `ModelingInputRecord` contracts with explicit model-ready feature and target sets
- added a synchronous `LinearListingPipelineService` that composes scraper,
  normalization, enrichment, and modeling in one in-process sequence without
  replacing the existing raw-only acquisition workflow
- added regression tests that cover stage handoff contracts across the full linear
  pipeline and keep the modeling boundary isolated from upstream non-enriched inputs

### Changed

- replaced the modeling placeholder contract with a typed schema that includes
  `model_version`, `modeling_input_version`, explicit modeling metadata, and full
  enriched-record traceability for downstream consumers
- updated module documentation to mark the modeling package as an active stage with
  a concrete runtime component

## [1.2.0] - 2026-03-17

### Added

- added a deterministic enrichment-stage `NormalizedListingEnricher` component that
  accepts `NormalizedListingRecord` inputs only and emits stable
  `EnrichedListingRecord` contracts
- added explicit derived price and property feature contracts for parsed asking
  price, disposition, floor area, price per square meter, and stage-level boolean
  flags needed by downstream modeling work

### Changed

- replaced the enrichment placeholder contract with a typed schema that includes an
  `enrichment_version` field, preserves the full normalized input record for
  traceability, and documents the initial V1 feature derivations
- expanded module and unit-test coverage so enrichment remains isolated from
  scraper-stage contracts and normalization behavior

## [1.1.0] - 2026-03-17

### Added

- added a normalization-stage `RawListingNormalizer` component that converts
  scraper-owned `RawListingRecord` snapshots into stable `NormalizedListingRecord`
  contracts with explicit provenance metadata
- added explicit normalized price, building, and location sub-contracts plus
  deterministic regression tests for representative normalization mappings

### Changed

- replaced the placeholder normalization contract with a stable typed schema that
  includes `normalization_version`, preserves unmapped raw fields under
  `source_specific_attributes`, and represents missing typed values as `None`

## [1.0.9] - 2026-03-17

### Added

- added a scraper-owned `RawListingCollector` service that emits `RawListingRecord`
  contracts before persistence, keeping raw contract construction inside the scraper
  stage boundary

### Changed

- tightened the raw scraper payload contract to explicit JSON-compatible value types
  and removed the storage-oriented `backend` field from raw source metadata
- refactored `RawAcquisitionService` to orchestrate scraper-emitted raw records
  instead of constructing persistence-shaped records itself
- expanded unit coverage to prove emitted scraper outputs remain source-faithful,
  JSON-serializable, and free of downstream normalized or derived fields

## [1.0.8] - 2026-03-17

### Changed

- removed the temporary `scraperweb.scraping` compatibility package and updated the
  codebase to import scraper clients and parsers directly from `scraperweb.scraper`
- removed `scraperweb.persistence.models` so raw-contract ownership now exists only
  under `scraperweb.scraper.models`, reducing duplicate module surfaces inside
  `scraperweb`

## [1.0.7] - 2026-03-17

### Added

- added explicit `scraperweb.scraper`, `scraperweb.normalization`,
  `scraperweb.enrichment`, and `scraperweb.modeling` package boundaries with typed
  stage-contract modules for the planned linear pipeline
- added regression tests that enforce one-way stage dependencies across the new
  pipeline packages

### Changed

- moved canonical raw-contract ownership to `scraperweb.scraper.models` and updated
  the active runtime to import scraper-stage clients, parsers, and contracts from the
  new package boundary
- converted `scraperweb.scraping.*` and `scraperweb.persistence.models` into
  documented compatibility wrappers so the CLI and raw persistence path keep working
  during the transition

## [1.0.6] - 2026-03-17

### Changed

- approved and documented the in-repo modular pipeline target architecture with
  explicit `scraper`, `normalization`, `enrichment`, and `modeling` stage boundaries
- defined one-way stage dependencies, typed stage-boundary contracts, and module
  ownership rules in the architecture and module documentation
- synchronized package version metadata so `pyproject.toml` and `scraperweb.__version__`
  expose the same release version

## [1.0.5] - 2026-03-17

### Changed

- refined backlog tasks `TASK-010` through `TASK-015` with additive architectural guardrails for typed stage contracts, module ownership, dependency direction, stage version fields, raw-contract serialization, normalization idempotence, and contract-only pipeline handoffs

## [1.0.4] - 2026-03-17

### Added

- added a new `project/backlog/` task set for migrating the repository toward a simple modular pipeline with `scraper`, `normalization`, `enrichment`, and `modeling` stages

### Changed

- aligned the project planning backlog with the existing task template and explicit stage dependencies for the modular pipeline migration

## [1.0.3] - 2026-03-17

### Changed

- moved the test suite under a single `tests/` tree split into `tests/unit/` and `tests/integration/`, keeping shared fixtures under `tests/`

## [1.0.2] - 2026-03-17

### Added

- added an opt-in `integration_tests/` suite with a live Sreality runtime test that downloads and processes one real listing through the production clients, parsers, acquisition service, and filesystem repository

### Changed

- separated pytest discovery for deterministic unit tests and live integration tests, and documented how to enable the live suite explicitly

## [1.0.1] - 2026-03-17

### Added

- added representative HTML fixtures plus regression tests for scraping clients and parser contracts
- added CLI tests for MongoDB runtime selection and Typer-enforced bounded runtime options

### Changed

- expanded raw storage and acquisition service coverage to verify path sanitization, immutable raw payload persistence, and runtime stop conditions

## [1.0.0] - 2026-03-17

### Changed

- narrowed the supported runtime surface to raw listing acquisition and raw persistence only
- simplified runtime configuration to MongoDB values used for raw storage selection
- updated operator documentation to remove enrichment and auxiliary loader workflows

### Removed

- removed the `load-towns` and `load-districts` CLI commands and their legacy runtime modules
- removed geocoding-specific settings and the `geopy` dependency from the active runtime path

## [0.2.1] - 2026-03-17

### Changed

- removed legacy compatibility wrappers and compatibility-only entrypoints so the package exposes only the current CLI and module surface
- updated parser tests and operator documentation to target the active implementation instead of transitional aliases

### Removed

- removed compatibility modules `scraperweb.main`, `scraperweb.cities_data`, and `scraperweb.districts`
- removed compatibility-only Poetry script entrypoints and legacy wrapper scripts
- removed obsolete `SCRAPER_API_URL` configuration and the unused HTTP JSON-post helper

## [0.2.0] - 2026-03-17

### Added

- added a Typer-based `scraperweb` CLI with explicit `scrape`, `load-towns`, and `load-districts` commands
- added CLI regression tests covering scraper command option handling and auxiliary loader command dispatch

### Changed

- replaced the primary Poetry script entrypoint with the new Typer application while keeping legacy loader entrypoints as compatibility wrappers
- refactored runtime option parsing into reusable validation helpers so CLI handlers stay thin and service-oriented
- documented the raw-data-only CLI contract and updated operator usage examples in `README.md`

## [0.1.9] - 2026-03-17

### Added

- added `scraperweb.persistence` with canonical raw-record models plus filesystem and MongoDB storage adapters
- added historical snapshot persistence keyed by `listing_id` and `captured_at_utc` to preserve longitudinal price data for later analysis
- added repository tests covering filesystem storage, MongoDB index setup, and raw acquisition record construction

### Changed

- refactored `scraperweb.application.acquisition_service.RawAcquisitionService` to build immutable `RawListingRecord` objects and persist them through a storage abstraction
- updated `scraperweb.estate_scraper` to select persistence backends without changing orchestration flow
- documented operational tradeoffs and generated artifact layout for filesystem and MongoDB raw storage backends

## [0.1.8] - 2026-03-17

### Added

- added `scraperweb.scraping.clients` with dedicated HTTP client classes for listing and detail page retrieval
- added `scraperweb.scraping.parsers` with dedicated listing-page and detail-page parser classes
- added `scraperweb.application.acquisition_service.RawAcquisitionService` for explicit orchestration of discovery and detail record collection

### Changed

- refactored `scraperweb.estate_scraper` to compose runtime behavior from injected services instead of a single procedural flow
- moved record delivery side effects behind `EstateRecordProcessor`, keeping parser classes side-effect free
- preserved compatibility helper functions (`get_range_of_estates`, `get_list_of_estates`, `get_final_data_for_estate_to_database`) by delegating them to the new classes

## [0.1.7] - 2026-03-17

### Added

- documented target application layers for CLI, orchestration, scraping/parsing, and persistence in `docs/ARCHITECTURE.md`
- documented the raw record contract (`RawListingRecord`) with explicit exclusions for enrichment, normalization, and derived fields
- documented target core interfaces and planned concrete adapters aligned to SOLID boundaries

### Changed

- updated `docs/MODULES.md` with target layered module boundaries for the refactor
- identified transitional modules and replacement/removal direction for the raw-data architecture migration

## [0.1.6] - 2026-03-17

### Added

- added a dedicated `scraperweb.cli_runtime_options` module that defines runtime CLI options for region selection, page limits, estate limits, and storage backend selection
- added parser validation for backend-specific option constraints to keep the future Typer CLI contract explicit and testable
- added deterministic tests for runtime option defaults, limit parsing, and backend option compatibility checks

### Changed

- updated `scraperweb.estate_scraper` entrypoint to parse and apply region/page/estate runtime limits
- documented required, optional, and mutually constrained runtime options in `README.md`

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
