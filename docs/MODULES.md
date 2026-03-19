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

### `scraperweb.scraper`

Canonical scraper-stage package for raw contracts, HTTP clients, and HTML parsers.
`RawListingRecord` ownership now lives here.

Status: active package boundary.
Parser assumptions: listing pages must expose at least one detail-page link, and
detail pages must preserve a non-empty `h1` title plus at least one aligned
`dt/dd` attribute pair before raw scraper payloads are accepted.

### `scraperweb.normalization`

Canonical normalization-stage package for typed output contracts and deterministic
raw-to-normalized mapping services.

Status: active package boundary with `RawListingNormalizer`, a stable normalized
record contract, and a filesystem-backed operator workflow for replaying persisted
raw snapshots into normalized JSON artifacts. Missing known values are represented
as `None`, partially parsed composite values leave unresolved typed fields as
`None`, and unmapped raw source fields remain under `source_specific_attributes`.
Location normalization now maps `Lokalita:` into a dedicated typed field and marks
title-derived municipality or district values explicitly as fallback provenance
instead of treating them as direct source facts. Core attribute normalization also
maps supported `Příslušenství:` fragments into `core_attributes.accessories`,
including elevator, accessibility, furnishing, balcony/loggia/terrace/cellar, and
parking-capacity semantics while preserving unsupported fragments explicitly.
This boundary intentionally stops before any reference-data join. Municipality
codes, region codes, ORP codes, resolved coordinates, geocoding precision,
geocoding confidence, district-center membership, and spatial buckets are
approved as enrichment-owned derived features, not normalization output fields.
Normalization may still add replayable geocoding input fragments such as a
canonical query string, parsed house number, or source-backed address text in a
later implementation task because those remain normalized inputs rather than
geocoding results.

### `scraperweb.enrichment`

Canonical enrichment-stage package for typed output contracts and deterministic
derived-feature services built on normalized records only.

Status: active package boundary with `NormalizedListingEnricher`, a stable
enriched record contract, and a filesystem-backed operator workflow for
replaying persisted normalized snapshots into enriched JSON artifacts. The
current feature set stays explicit and deterministic, while preserving the full
normalized input record for traceability. Enrichment now derives canonical area
and area-based price-density features from `normalized_record.area_details`
only, keeping `floor_area_sqm` as a compatibility alias of the canonical area
value. It also derives conservative building semantics from
`normalized_record.core_attributes.building`, including ground-floor and
upper-floor flags, a relative floor-position bucket, and coarse material and
condition buckets. Enrichment also owns a dedicated `location_features`
sub-contract that joins bundled reference datasets from `data/` and exposes
explicit match status, administrative identifiers, municipality centroid
coordinates, macro distances to district cities and district-local ORP centers,
district-city and ORP-center flags, metropolitan district overrides, Prague
spatial buckets, nearby-place accessibility aggregates, conservative district
normalization, and the future multi-level geocoding contract for resolved
coordinates, precision, confidence, fallback level, and provider provenance.

### `scraperweb.modeling`

Canonical modeling-stage package for typed output contracts and deterministic
model-ready input builders.

Status: active package boundary with `EnrichedListingModelingInputBuilder` and a
stable modeling input contract that depends on enrichment outputs only.
The current contract now promotes the approved stable location subset from
enrichment into `ModelingFeatureSet`, including administrative identifiers,
metropolitan buckets, coordinates, macro-distance metrics, district-center
flags, and nearby-place accessibility aggregates. Match candidates and other
traceability-only metadata remain enrichment-only and are available through the
preserved `enriched_record`. Future geocoding-specific flattening should stay
limited to stable fields such as coordinates, precision, confidence, and
fallback booleans rather than replay-oriented input text.

### `scraperweb.persistence`

Repository interfaces and storage adapters. Raw-contract ownership belongs to the
producing scraper stage, so persistence depends on scraper-owned models instead of
defining them locally.

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
