# Architecture

## Purpose

`scraperweb` is a Python application for:

- downloading raw listing data from `sreality.cz`
- preserving the downloaded content without modifying the payload
- keeping the persistence layer simple and replaceable

The project goal is raw data acquisition. Data transformations, enrichment, or
business-level normalization are outside the intended scope of the scraper itself.

## Runtime Shape

The project is intentionally split into four top-level areas:

- `scraperweb/`: importable application modules
- `scripts/`: thin executable wrappers
- `data/`: CSV source datasets
- `docs/`: technical documentation and generated API docs

## Target Application Layers

The target design is layered so dependencies always point inward toward stable
abstractions:

1. CLI layer
2. Application orchestration layer
3. Scraping and parsing layer
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

- coordinate the raw acquisition workflow
- request list pages and detail pages through injected scraper ports
- stream raw records to the selected persistence port
- enforce high-level runtime constraints (regions, limits, stop conditions)

Rules:

- business flow only, no storage/backend-specific details
- uses constructor-injected dependencies only

### 3) Scraping and parsing layer

Responsibilities:

- perform HTTP retrieval of list/detail pages
- extract listing identifiers and raw payload from HTML
- produce only raw record objects that mirror source content

Rules:

- parser outputs must not include enrichment or derived data
- HTML parsing logic is isolated from orchestration

### 4) Persistence layer

Responsibilities:

- persist raw records in backend-specific form
- expose a stable write contract to the orchestration layer
- support multiple implementations (MongoDB, filesystem)

Rules:

- no parsing or transformation logic
- historical snapshot identity belongs here (for example, unique key on `listing_id` and `captured_at_utc`)

## Core Interfaces and Classes

The implementation tasks should align around these core abstractions:

- `RuntimeOptions`: immutable runtime input model used by CLI and orchestration
- `RawAcquisitionService`: application service that runs acquisition end-to-end
- `ListingPageClient`: port for downloading listing pages
- `ListingPageParser`: port for extracting listing ids/urls from listing pages
- `DetailPageClient`: port for downloading listing detail pages
- `DetailPageParser`: port for producing `RawListingRecord` from detail content
- `RawRecordRepository`: port for persisting raw records

Planned concrete implementations:

- `SrealityHttpClient`: HTTP adapter used by page clients
- `SrealityListingParser`: HTML parser adapter for listing pages
- `SrealityDetailParser`: HTML parser adapter for detail pages
- `MongoRawRecordRepository`: MongoDB persistence adapter
- `FilesystemRawRecordRepository`: filesystem persistence adapter

SOLID alignment:

- Single Responsibility: HTTP, parsing, orchestration, and persistence are split.
- Open/Closed: new storage adapters implement `RawRecordRepository`.
- Liskov Substitution: repositories and parsers are swappable via interfaces.
- Interface Segregation: read/download/parse/write contracts stay focused.
- Dependency Inversion: orchestration depends on abstract ports only.

## Raw Record Contract

`RawListingRecord` is the canonical payload moving from parsing to persistence.

Required fields:

- `listing_id`: source identifier from `sreality.cz`
- `source_url`: detail page URL
- `captured_at_utc`: capture timestamp
- `source_payload`: raw extracted payload (JSON-like mapping and/or raw HTML)
- `source_metadata`: capture metadata (parser version, HTTP status, region/page context)

Optional fields:

- `raw_page_snapshot`: raw detail-page HTML stored without transformation when snapshot capture is enabled

Explicit exclusions (must not appear in raw record contract):

- geocoding results
- address normalization
- postcode/district enrichment
- business-level transformations
- computed analytics or derived summary fields

## Main Flows

### Estate scraping flow

1. `scraperweb.estate_scraper` builds runtime configuration from environment.
2. Listing pages are fetched from `sreality.cz`.
3. Estate detail pages are downloaded and parsed into a raw machine-readable form.
4. The captured records are stored without additional data operations.

The storage target is intentionally not fixed yet. The architecture must support:

- MongoDB for document-oriented raw record storage
- filesystem storage for raw JSON or HTML snapshots

The selected persistence strategy for the current implementation is historical
snapshot storage. Each capture is immutable and identified by the combination of
`listing_id` and `captured_at_utc` so later analytical pipelines can reconstruct
price changes over time.

### Reference data loading flow

1. `scraperweb.towns` reads city datasets from `data/`.
2. `scraperweb.districts_loader` reads postcode coordinates from `data/souradnice.csv`.
3. Records are prepared for auxiliary use when the selected storage or runtime model
   requires them.

## Configuration

Runtime configuration is centralized in `scraperweb.config` and uses:

- `MONGODB_URI`
- `MONGODB_DATABASE`
- `SCRAPER_API_URL`
- `GEOPY_USER_AGENT`

Some of these variables belong to the current implementation and may become obsolete as
the project is reduced to raw extraction and storage only.

## Transitional Modules and Replacement Plan

These modules are transitional and should be removed or replaced during the refactor:

- `scraperweb.estate_scraper`: currently a mixed procedural runtime; replace with thin
  CLI adapter plus `RawAcquisitionService` orchestration.
- `scraperweb.main`: compatibility wrapper; remove once new CLI entrypoint is stable.
- `scraperweb.cities_data`: legacy compatibility wrapper; remove after raw-only flow no
  longer imports legacy names.
- `scraperweb.districts`: legacy compatibility wrapper; remove after raw-only flow no
  longer imports legacy names.

Potentially obsolete for raw-only scope and subject to follow-up decision:

- `scraperweb.towns`
- `scraperweb.districts_loader`

These two loaders should remain until tasks explicitly removing enrichment/reference-data
flows are completed.

## Constraints

- Scraping depends on external HTML structure at `sreality.cz`.
- The scraper should avoid mutating source data during capture.
- The final persistence decision between MongoDB and filesystem storage is still open.
