# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and the project uses Semantic Versioning.

## [1.12.2] - 2026-03-18

### Added

- added backlog tasks `TASK-029` through `TASK-034` to break the remaining
  enrichment-stage roadmap work into explicit deliverables covering typed
  area-based pricing, building semantics, accessories, nearby-place
  accessibility, lifecycle freshness, and an operator-facing enrichment replay
  workflow

## [1.12.1] - 2026-03-18

### Added

- added representative normalization replay validation for persisted raw
  snapshots that exercise both `location.nearby_places` and
  `core_attributes.accessories` in serialized filesystem artifacts

### Changed

- updated operator-facing documentation to record artifact validation
  expectations, canonical access paths for nearby places and accessories, and
  the current decision to defer downstream consumption of these typed fields in
  enrichment and modeling
- recorded migration guidance for normalized artifacts so reviewers can verify
  that mapped nearby-place keys and `Příslušenství:` values no longer remain in
  `core_attributes.source_specific_attributes` after replay

## [1.12.0] - 2026-03-18

### Added

- added typed `core_attributes.accessories` normalization output with explicit
  elevator, barrier-free access, furnishing state, balcony/loggia/terrace/cellar,
  and parking-space capacity fields sourced from `Příslušenství:`
- added focused accessories regression coverage for duplicated leading fragments,
  measured accessory features, parking counts, and ambiguous fragments such as
  `2 garáže`

### Changed

- changed normalization outputs to version `normalized-listing-v6` so supported
  accessories now map into the canonical core-attributes contract instead of
  remaining only under `source_specific_attributes`

## [1.11.1] - 2026-03-18

### Added

- added the approved design for normalized accessories support, including the
  `core_attributes.accessories` contract shape, shared area-feature sub-model,
  conservative fallback rules, and the planned normalization contract bump to
  `normalized-listing-v6`

## [1.11.0] - 2026-03-18

### Added

- added typed `location.nearby_places` normalization output with explicit
  `category`, `source_key`, `source_text`, `name`, and `distance_m` fields for
  supported nearby-place payload keys
- added focused nearby-place regression coverage for persisted raw snapshots and
  malformed-but-supported source values so normalization keeps traceability

### Changed

- changed normalization outputs to version `normalized-listing-v5` so supported
  nearby-place keys now map into the canonical location contract instead of
  remaining only under `core_attributes.source_specific_attributes`

## [1.10.2] - 2026-03-18

### Added

- added the approved design for normalized nearby-place support, including the
  `location.nearby_places` contract shape, overflow coexistence rules, parser
  fallback strategy, and the planned normalization contract bump to
  `normalized-listing-v5`

## [1.10.1] - 2026-03-18

### Added

- added backlog tasks for designing and implementing normalized nearby-place
  parsing and structured accessories parsing, including a follow-up replay and
  documentation task for the resulting schema evolution

## [1.10.0] - 2026-03-18

### Added

- added derived enrichment features for normalized building and energy fields,
  including optional `is_top_floor`, `is_new_build`, and
  `energy_efficiency_bucket` semantics alongside the existing price metrics
- added focused enrichment regression coverage built from normalized record
  fixtures so derived feature behavior stays deterministic without raw payload
  parsing

### Changed

- changed enrichment outputs to version `enriched-listing-v2` so the canonical
  contract now exposes the new building and energy derived features while
  preserving the full normalized source record for traceability
- changed modeling inputs to version `modeling-input-v2` so downstream
  consumers receive the new derived building and energy features at the
  modeling boundary
- changed asking-price derivation to rely on normalized typed monetary fields
  only instead of reparsing preserved raw price text during enrichment

## [1.9.0] - 2026-03-18

### Added

- added typed normalized price fields for Czech listing prices, including parsed
  integer `amount_czk`, explicit `currency_code`, and deterministic
  `pricing_mode` while preserving the original source text
- added structured normalized building and energy contracts with source text,
  floor position metadata, physical condition, underground floor counts, energy
  regulation references, and consumption values parsed directly from raw detail
  payloads
- added focused normalization regression coverage for representative
  `data/raw/all-czechia` snapshots covering fixed-price listings, on-request
  pricing, richer building layouts, energy descriptors, and partially parsed
  building fragments

### Changed

- changed normalization outputs to version `normalized-listing-v4` so explicit
  typed price, building, and energy fields are now emitted in the canonical
  contract instead of overloading `building.condition` or leaving price and
  energy mostly as raw text
- changed enrichment price resolution to prefer normalized typed price amounts
  and to fall back to legacy text parsing only when typed price data is missing

## [1.8.3] - 2026-03-18

### Changed

- updated `docs/ROADMAP.md` so the pipeline and operations checklist now reflects
  the shipped normalization replay workflow and normalized filesystem artifact
  persistence as completed work, while narrowing the remaining persistence
  decisions to enrichment, modeling, and possible backend expansion

## [1.8.2] - 2026-03-18

### Added

- added a public `scraperweb normalize` CLI workflow that replays persisted raw
  filesystem snapshots into normalized JSON artifacts scoped by region,
  listing id, or scrape run id
- added filesystem-backed normalization workflow services and integration-style
  tests that exercise representative raw fixtures derived from
  `data/raw/all-czechia`

### Changed

- changed generated artifacts documentation to include normalized filesystem
  outputs and their traceability guarantees
- changed roadmap and module documentation so normalization is now documented as
  a supported operator-facing workflow instead of an internal-only stage

## [1.8.1] - 2026-03-18

### Added

- added typed location descriptor and per-field provenance metadata so normalized
  location values now distinguish direct `Lokalita:` payload facts from
  title-derived fallback values
- added regression coverage for representative Prague and non-Prague title
  patterns from `data/raw/all-czechia`, including titles without a comma
  separator before the location suffix

### Changed

- changed location normalization to prefer dedicated raw payload fields where
  available and to isolate remaining title parsing behind documented fallback
  rules instead of the previous naive comma split
- changed Prague numbered-district fallback parsing so municipality identity now
  normalizes to `Praha` while keeping the district name in `city_district`

## [1.8.0] - 2026-03-18

### Added

- added grouped normalized fields for area details, ownership, listing
  lifecycle dates, and source listing references derived directly from the
  Sreality detail payload
- added regression coverage for representative `data/raw/all-czechia`
  snapshots and partial area parsing so mapped fields remain deterministic and
  traceable

### Changed

- changed normalization to parse supported `Plocha:` fragments into explicit
  typed area fields while preserving unsupported fragments in the normalized
  contract instead of leaving the raw text only in source-specific overflow
- changed normalization overflow handling so `Vlastnictví:`, `ID zakázky:`,
  `Vloženo:`, and `Upraveno:` now map into dedicated typed sub-contracts
  instead of remaining under `source_specific_attributes`

## [1.7.7] - 2026-03-18

### Added

- added backlog tasks `TASK-019` through `TASK-021` to break the remaining
  normalization-stage roadmap work into explicit deliverables grounded in the
  current `data/raw/all-czechia` payload coverage

## [1.7.6] - 2026-03-18

### Fixed

- fixed detail-page parsing so empty optional `dd` rows no longer cause the
  whole listing to be rejected; the scraper now skips empty values and keeps
  parsing the remaining attributes

## [1.7.5] - 2026-03-18

### Added

- added persisted detail-page markup failure artifacts so skipped listings now
  store the raw failed HTML snapshot and serialized failure metadata for later
  diagnostics in both filesystem and MongoDB backends

## [1.7.4] - 2026-03-18

### Changed

- changed default scraper recovery so detail-page markup validation failures are
  now logged and skipped per listing instead of terminating the whole region run
- changed terminal progress reporting to show skipped listings caused by detail
  markup failures in addition to skipped HTTP failures

## [1.7.3] - 2026-03-17

### Added

- added terminal progress reporting so default scraper runs now announce start,
  per-page activity, periodic processed-estate counts, skipped detail failures,
  and region completion
- added `--verbose` and `--quiet` CLI options to control scraper progress output

### Changed

- changed CLI runtime option validation to reject conflicting `--verbose` and
  `--quiet` combinations
- changed scraper runtime composition to inject a dedicated progress reporter
  instead of relying only on logger output for operator visibility

## [1.7.2] - 2026-03-17

### Added

- added a `--fail-on-http-error` CLI option for debug runs that should stop on
  the first scraper HTTP failure

### Changed

- changed the default scrape behavior so detail-page HTTP failures are logged and
  skipped instead of terminating the whole run
- changed the acquisition flow so scraper HTTP failures are logged by default
  without crashing the CLI unless fail-fast mode is explicitly enabled

## [1.7.1] - 2026-03-17

### Fixed

- fixed the default scrape behavior so runs without `--max-pages` no longer stop
  after the first listing page and instead continue across the all-Czechia
  listing target until scraper stop conditions are met

### Changed

- changed the `--max-pages` CLI option from a required default page cap to an
  optional traversal limit

## [1.7.0] - 2026-03-17

### Added

- added a global `all-czechia` scrape target that points to the nationwide
  apartment-sale listing URL on `sreality.cz`
- added regression coverage for the new default global target at both CLI and
  runtime-composition levels

### Changed

- changed the default CLI behavior so runs without `--region` now scrape the
  global all-Czechia apartment listing target instead of iterating region URLs
- replaced index-based region URL selection with explicit region-slug to listing
  URL mapping in the scraper runtime

## [1.6.0] - 2026-03-17

### Added

- added deterministic traversal regression coverage for repeated listing pages,
  empty listing pages, and pagination drift pages that contain no unseen estate
  URLs

### Changed

- replaced the collector's pagination-count traversal assumption with
  page-by-page stop conditions driven by observed listing-page outcomes
- documented the operator-visible region traversal stop conditions that now end a
  run on empty, repeated, or fully duplicated listing pages before `max_pages`

## [1.5.0] - 2026-03-17

### Added

- added parser-owned markup validation errors for listing and detail pages so
  missing detail links, missing titles, and malformed attribute sections fail
  explicitly instead of producing low-value raw payloads
- added fixture-based parser and collector tests that cover valid markup,
  missing listing links, missing detail titles, and misaligned detail
  attributes

### Changed

- updated the scraper runtime to translate parser validation failures into
  contextual scraper response errors with region, listing-page, and listing-URL
  metadata
- documented the minimum listing-page and detail-page structural assumptions
  that anchor the scraper-stage raw contract

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
