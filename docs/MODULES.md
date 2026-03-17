# Modules

## Target Module Boundaries

The refactor target is a layered module layout with inward dependency flow:

- `scraperweb.cli.*`: argument parsing and runtime option validation
- `scraperweb.application.*`: orchestration services and pipeline use cases
- `scraperweb.scraper.*`: HTTP clients, HTML parsers, scraper-stage services, and
  raw-record contracts
- `scraperweb.normalization.*`: normalization services and normalized-record contracts
- `scraperweb.enrichment.*`: enrichment services and enriched-record contracts
- `scraperweb.modeling.*`: modeling-input builders and modeling-input contracts
- `scraperweb.persistence.*`: repository interfaces and backend adapters

This structure is now partially implemented. The `scraper`, `normalization`,
`enrichment`, and `modeling` packages exist as explicit boundaries, while later-stage
runtime behavior is still implemented incrementally in follow-up tasks.

Approved dependency direction:

- `scraperweb.scraper` may not depend on `scraperweb.normalization`,
  `scraperweb.enrichment`, or `scraperweb.modeling`
- `scraperweb.normalization` may depend on `scraperweb.scraper` contracts only
- `scraperweb.enrichment` may depend on `scraperweb.normalization` contracts only
- `scraperweb.modeling` may depend on `scraperweb.enrichment` contracts only
- `scraperweb.application` may orchestrate all stages without owning stage contracts
- `scraperweb.persistence` may persist stage records but may not redefine them

## Package Modules

### `scraperweb.config`

Centralized runtime settings and path helpers.

### `scraperweb.cli`

Runtime entrypoints and option parsing. This layer converts external inputs into
typed runtime models and hands control to orchestration services.

### `scraperweb.application`

High-level orchestration for current raw acquisition and the future linear pipeline.
This layer wires stage components together but does not own stage contracts.

### `scraperweb.scraping`

Current implementation package for HTTP adapters and HTML parsers. This package is a
transitional compatibility layer that re-exports scraper-owned clients and parsers.

Status: transitional module pending cleanup after import sites are migrated.

### `scraperweb.scraper`

Canonical scraper-stage package for raw contracts, HTTP clients, and HTML parsers.
`RawListingRecord` ownership now lives here.

Status: active package boundary.

### `scraperweb.normalization`

Canonical normalization-stage package for typed output contracts.

Status: package boundary in place; transformation services follow in later tasks.

### `scraperweb.enrichment`

Canonical enrichment-stage package for typed output contracts.

Status: package boundary in place; transformation services follow in later tasks.

### `scraperweb.modeling`

Canonical modeling-stage package for typed output contracts.

Status: package boundary in place; modeling builders follow in later tasks.

### `scraperweb.persistence`

Repository interfaces and storage adapters. Current raw contracts live here
through compatibility re-exports, but canonical raw-contract ownership now belongs to
the producing scraper stage.

### `scraperweb.estate_scraper`

Primary scraping workflow for downloading raw estate listings from `sreality.cz` and
persisting them without transformation.

Status: transitional module pending replacement by layered services.

## Stage Contract Ownership

Every stage boundary must be represented by a typed Python model located inside the
module that produces it:

- `RawListingRecord` in `scraperweb.scraper.models`
- `NormalizedListingRecord` in `scraperweb.normalization.models`
- `EnrichedListingRecord` in `scraperweb.enrichment.models`
- `ModelingInputRecord` in `scraperweb.modeling.models`

Stage semantics:

- scraper collects raw facts only
- normalization produces stable structured data only
- enrichment computes derived features only
- modeling consumes enriched data only

Poetry also exposes:

- `scraperweb`
