# Architecture

## Purpose

`scraperweb` is a Python application for:

- downloading raw listing data from `sreality.cz`
- preserving source facts without mutating the captured payload
- structuring the repository so later processing stages can be added inside the
  same Python project

The current runtime remains focused on raw acquisition. The approved target
architecture extends that runtime into a simple in-repo pipeline with explicit
`scraper`, `normalization`, `enrichment`, and `modeling` boundaries.

## Runtime Shape

The project is intentionally split into four top-level areas:

- `scraperweb/`: importable application modules
- `data/`: CSV source datasets
- `docs/`: technical documentation and generated API docs

## Target Pipeline Architecture

The project keeps one repository and one Python package. No additional services,
brokers, workers, or external orchestrators are introduced. The pipeline is a
linear in-process flow:

1. `scraper`
2. `normalization`
3. `enrichment`
4. `modeling`

The dependency rule is one-way only:

`scraper -> normalization -> enrichment -> modeling`

Rules:

- each stage may depend only on its own module and the immediately previous stage
  contract
- downstream stages must not be imported by upstream stages
- persistence adapters may store stage outputs, but they must not redefine stage
  contracts
- each stage boundary contract must be implemented as a typed Python model
- contract ownership belongs to the stage module that produces the record

## Stage Responsibilities

### 1) Scraper stage

Purpose:

- collect raw facts from `sreality.cz`
- preserve source payloads and capture metadata
- avoid any business normalization or derived values

Output contract:

- `RawListingRecord`

Required contract fields:

- `listing_id`: source identifier from `sreality.cz`
- `source_url`: detail page URL
- `captured_at_utc`: capture timestamp
- `source_payload`: raw extracted payload
- `source_metadata`: capture context and parser metadata

Optional contract fields:

- `raw_page_snapshot`: optional raw HTML snapshot

Explicit exclusions:

- normalized address parts
- derived feature flags
- scoring inputs
- analytical summaries

### 2) Normalization stage

Purpose:

- convert raw source facts into a stable structured schema
- standardize field names, units, and null handling
- produce idempotent records from raw input

Input contract:

- `RawListingRecord`

Output contract:

- `NormalizedListingRecord`

Required contract fields:

- `listing_id`: carried forward stable record identity
- `source_url`: original detail page URL
- `captured_at_utc`: original capture timestamp
- `normalized_at_utc`: normalization timestamp
- `core_attributes`: stable typed property fields extracted from raw payload
- `location`: stable structured location fields derived from raw source facts only
- `normalization_metadata`: stage version and traceability metadata

Rules:

- normalization may reshape and clean source data
- normalization must not add external facts or computed business features

### 3) Enrichment stage

Purpose:

- compute derived features from normalized data
- attach deterministic attributes required by downstream analytics or modeling
- keep derivations reproducible and traceable

Input contract:

- `NormalizedListingRecord`

Output contract:

- `EnrichedListingRecord`

Required contract fields:

- `listing_id`: stable record identity
- `source_url`: original detail page URL
- `captured_at_utc`: original capture timestamp
- `normalized_record`: normalized structured data consumed by enrichment
- `derived_features`: computed attributes and feature values
- `enrichment_metadata`: stage version and derivation metadata

Rules:

- enrichment computes derived values only
- enrichment must not fetch new external source systems in this design step
- enrichment must preserve traceability back to normalized input

### 4) Modeling stage

Purpose:

- prepare enriched data for training, scoring, or analytical consumption
- define the final contract consumed by modeling-specific workflows

Input contract:

- `EnrichedListingRecord`

Output contract:

- `ModelingInputRecord`

Required contract fields:

- `listing_id`: stable record identity
- `captured_at_utc`: original capture timestamp
- `feature_vector`: modeling-ready fields derived only from enriched data
- `target_values`: optional supervised-learning targets when available
- `modeling_metadata`: stage version and dataset lineage metadata

Rules:

- modeling consumes enriched data only
- modeling must not read `RawListingRecord` or `NormalizedListingRecord` directly
- modeling-specific reshaping must remain separate from enrichment logic

## Target Application Layers

The target design is layered so dependencies always point inward toward stable
abstractions:

1. CLI layer
2. Application orchestration layer
3. Pipeline stage modules
4. Persistence layer

### 1) CLI layer

Responsibilities:

- parse runtime arguments and validate basic option constraints
- convert CLI inputs into typed runtime options
- hand off execution to a single application use case

Rules:

- no HTTP calls
- no HTML parsing
- no direct storage logic

### 2) Application orchestration layer

Responsibilities:

- coordinate the active pipeline workflow
- request list pages and detail pages through injected scraper ports
- invoke later stages in linear order when they are implemented
- stream stage records to the selected persistence port
- enforce high-level runtime constraints (regions, limits, stop conditions)

Rules:

- business flow only, no storage/backend-specific details
- uses constructor-injected dependencies only

### 3) Pipeline stage modules

Responsibilities:

- isolate stage-specific models, services, and transformation rules
- expose explicit typed record contracts at every stage boundary
- keep stage responsibilities narrow and one-directional

Rules:

- scraper produces raw facts only
- normalization produces stable structured data only
- enrichment computes derived features only
- modeling consumes enriched data only

### 4) Persistence layer

Responsibilities:

- persist stage records in backend-specific form
- expose a stable write contract to the orchestration layer
- support multiple implementations (MongoDB, filesystem)

Rules:

- no parsing or transformation logic
- historical snapshot identity belongs here (for example, unique key on `listing_id`
  and `captured_at_utc`)

## Core Interfaces and Classes

The implementation tasks should align around these core abstractions:

- `RuntimeOptions`: immutable runtime input model used by CLI and orchestration
- `PipelineRunService`: application service that coordinates the linear pipeline
- `RawAcquisitionService`: scraper-stage application service for acquisition
- `ListingPageClient`: port for downloading listing pages
- `ListingPageParser`: port for extracting listing ids/urls from listing pages
- `DetailPageClient`: port for downloading listing detail pages
- `DetailPageParser`: port for producing `RawListingRecord` from detail content
- `Normalizer`: component that converts `RawListingRecord` to `NormalizedListingRecord`
- `Enricher`: component that converts `NormalizedListingRecord` to
  `EnrichedListingRecord`
- `ModelingInputBuilder`: component that converts `EnrichedListingRecord` to
  `ModelingInputRecord`
- `RawRecordRepository`: port for persisting raw records

Planned concrete implementations:

- `SrealityHttpClient`: HTTP adapter used by page clients
- `SrealityListingParser`: HTML parser adapter for listing pages
- `SrealityDetailParser`: HTML parser adapter for detail pages
- `MongoRawRecordRepository`: MongoDB persistence adapter
- `FilesystemRawRecordRepository`: filesystem persistence adapter

SOLID alignment:

- Single Responsibility: stage logic, orchestration, parsing, and persistence are split.
- Open/Closed: new stage implementations and storage adapters extend interfaces.
- Liskov Substitution: repositories and stage processors are swappable via contracts.
- Interface Segregation: each stage exposes a narrow input/output boundary.
- Dependency Inversion: orchestration depends on typed stage contracts and abstract ports.

## Target Module Ownership

The approved package ownership for follow-up implementation tasks is:

- `scraperweb.scraper.*`: raw scraping clients, parsers, scraper-stage services, and
  `RawListingRecord`
- `scraperweb.normalization.*`: normalization components and
  `NormalizedListingRecord`
- `scraperweb.enrichment.*`: enrichment components and `EnrichedListingRecord`
- `scraperweb.modeling.*`: modeling-input builders and `ModelingInputRecord`
- `scraperweb.application.*`: orchestration that wires stages together
- `scraperweb.persistence.*`: repositories and backend adapters
- `scraperweb.cli.*`: runtime entrypoints and option parsing

Each contract and component must live in the module boundary that owns its stage.
Cross-stage helpers should be introduced only when they are stage-agnostic and do
not weaken the one-way dependency rule.

## Main Flows

### Current runtime flow

1. `scraperweb.cli` validates runtime options for a raw scraping run.
2. Listing pages are fetched from `sreality.cz`.
3. Estate detail pages are downloaded and parsed into a raw machine-readable form.
4. The captured records are stored without additional data operations.

### Target pipeline flow

1. `scraperweb.cli` validates runtime options for a pipeline run.
2. The scraper stage emits `RawListingRecord`.
3. The normalization stage converts the raw record into `NormalizedListingRecord`.
4. The enrichment stage converts the normalized record into `EnrichedListingRecord`.
5. The modeling stage converts the enriched record into `ModelingInputRecord`.
6. Persistence adapters store whichever stage output the active use case requires.

The storage target is intentionally not fixed yet. The architecture must support:

- MongoDB for document-oriented raw record storage
- filesystem storage for raw JSON or HTML snapshots

The selected persistence strategy for the current implementation is historical
snapshot storage. Each capture is immutable and identified by the combination of
`listing_id` and `captured_at_utc` so later analytical pipelines can reconstruct
price changes over time.

## Configuration

Runtime configuration is centralized in `scraperweb.config` and uses:

- `MONGODB_URI`
- `MONGODB_DATABASE`

## Transitional Modules and Replacement Plan

These modules remain transitional and should still be simplified during future cleanup:

- `scraperweb.estate_scraper`: currently a mixed procedural runtime; replace with thin
  CLI adapter plus `RawAcquisitionService` orchestration.
- `scraperweb.persistence.models`: currently hosts the raw stage contract; move
  `RawListingRecord` ownership under `scraperweb.scraper` when the stage packages are
  introduced.

## Constraints

- Scraping depends on external HTML structure at `sreality.cz`.
- The scraper should avoid mutating source data during capture.
- The final persistence decision between MongoDB and filesystem storage is still open.
