---
task: TASK-041
status: "done"
priority: P1
type: design
---

# Design a multi-level geocoding contract

Task: TASK-041
Status: done
Priority: P1
Type: design
Author:
Created: 2026-03-19
Related: TASK-040

## Problem

The current location intelligence layer stores municipality-centroid coordinates
only, which is too coarse for price-surface analysis and too ambiguous for
street-level listings. Before implementing richer geospatial logic, the project
needs an explicit contract for address-derived coordinates, fallback coordinates,
precision, confidence, and provenance so downstream enrichment and modeling stay
deterministic.

## Definition of Done

- [x] Define the canonical normalized and/or enriched geocoding fields needed for
      multiple spatial precision levels, including exact-address, street,
      district, and municipality fallbacks where applicable.
- [x] Specify explicit fields for `location_precision`, `geocoding_source`,
      `geocoding_confidence`, and any text inputs preserved for traceability.
- [x] Decide which geocoding attributes belong in normalization, which belong in
      enrichment, and which should remain modeling-only derived helpers.
- [x] Document acceptable fallback behavior when only partial address data is
      available and when geocoding remains unresolved.
- [x] Define artifact and versioning implications for the approved contract.

## Notes

- The contract must let later stages distinguish precise coordinates from coarse
  municipality centroids without inferring that distinction indirectly.
- Confidence should stay explicit and machine-readable rather than embedded in
  free-text notes.
- Preserve enough source text to support later geocoder swaps or replay runs.

## Design Decision

Multi-level geocoding should stay split across normalization, enrichment, and
modeling rather than collapsing into one stage.

Normalization keeps only source-backed address text and provenance that come
directly from the listing payload or deterministic title parsing. Enrichment
owns all geocoding outputs, fallback resolution, quality metadata, and
coordinate provenance because those values depend on reference-backed or
provider-backed interpretation instead of raw source facts. Modeling should
flatten only the stable geocoding outputs that prove useful for downstream
features, while keeping replay and audit metadata inside enrichment.

This design extends the existing location-intelligence contract with an explicit
geocoding sub-contract instead of overloading municipality centroid fields to
implicitly represent all coordinate quality levels.

## Proposed Contract Ownership

### Normalization

`NormalizedLocation` should remain the canonical source-backed address input
contract and should add only traceable inputs needed for later geocoding:

- `street`
- `street_source`
- `city`
- `city_source`
- `city_district`
- `city_district_source`
- `location_text`
- `location_text_source`
- `location_descriptor`
- `location_descriptor_source`
- `geocoding_query_text: str | None`
- `geocoding_query_text_source: str | None`
- `house_number: str | None`
- `house_number_source: str | None`
- `address_text: str | None`
- `address_text_source: str | None`

`geocoding_query_text` should be a deterministic normalization-owned helper that
concatenates the best available structured address parts into one replayable
query string. It is still a source-backed text helper, not a geocoding result.
When house number or full address text cannot be parsed reliably from the
listing, those fields must remain `None` rather than guessed.

Normalization must not emit latitude, longitude, precision, confidence,
provider names, or fallback-stage decisions.

### Enrichment

Enrichment should own one explicit geocoding group inside
`EnrichedLocationFeatures`. The approved canonical fields are:

- `latitude: float | None`
- `longitude: float | None`
- `location_precision: str | None`
- `geocoding_source: str | None`
- `geocoding_confidence: str | None`
- `geocoding_match_strategy: str | None`
- `geocoding_query_text: str | None`
- `geocoding_query_text_source: str | None`
- `resolved_address_text: str | None`
- `resolved_street: str | None`
- `resolved_house_number: str | None`
- `resolved_city_district: str | None`
- `resolved_municipality_name: str | None`
- `resolved_municipality_code: str | None`
- `resolved_region_code: str | None`
- `geocoding_fallback_level: str | None`
- `geocoding_is_fallback: bool | None`

The controlled vocabulary should stay machine-readable and explicit:

- `location_precision`: `address`, `street`, `district`, `municipality`,
  `unresolved`
- `geocoding_confidence`: `high`, `medium`, `low`, `none`
- `geocoding_fallback_level`: `none`, `street`, `district`, `municipality`,
  `unresolved`

`geocoding_source` identifies the coordinate source used for the resolved point,
for example a future external geocoder, a district reference override, or the
existing municipality centroid dataset. `geocoding_match_strategy` records the
deterministic rule path that selected the final point, such as
`address_exact`, `street_centroid`, `district_override`, or
`municipality_centroid`.

Existing municipality administrative fields remain valid enrichment outputs and
should continue to coexist with the new geocoding fields. They describe
administrative identity; the geocoding fields describe coordinate quality and
provenance.

### Modeling

Modeling should not own raw traceability fields such as input query text,
resolved address text, or provider-specific source labels unless a later task
proves they are stable training features. The approved modeling-only candidates
for later flattening are:

- `latitude`
- `longitude`
- `location_precision`
- `geocoding_confidence`
- `geocoding_is_fallback`

Modeling may also derive helper booleans such as `has_precise_geocoding` or
precision buckets, but those should remain modeling-owned derived helpers rather
than enrichment-owned contract fields.

## Fallback And Unresolved Behavior

The fallback ladder must be deterministic and visible in the contract:

1. Exact address geocoding when street and house-number level inputs are present
   and resolve cleanly.
2. Street-level fallback when a reliable street is available but house number is
   missing or the exact address cannot be resolved.
3. District-level fallback when municipality identity is known and a supported
   district override can be resolved more precisely than the municipality
   centroid.
4. Municipality-level fallback when only municipality identity is resolved.
5. Unresolved when no approved location match can be produced.

Required behavior by outcome:

- Exact address resolution sets `location_precision` to `address`,
  `geocoding_fallback_level` to `none`, and `geocoding_is_fallback` to `False`.
- Street-level resolution sets `location_precision` to `street`,
  `geocoding_fallback_level` to `street`, and `geocoding_is_fallback` to
  `True`.
- District-level resolution sets `location_precision` to `district`,
  `geocoding_fallback_level` to `district`, and `geocoding_is_fallback` to
  `True`.
- Municipality-centroid resolution sets `location_precision` to `municipality`,
  `geocoding_fallback_level` to `municipality`, and `geocoding_is_fallback` to
  `True`.
- Unresolved listings keep coordinates empty, set `location_precision` to
  `unresolved`, set `geocoding_confidence` to `none`, and set
  `geocoding_fallback_level` to `unresolved`.

Confidence must never be inferred from the fallback level alone. A street-level
match may still be `medium` or `low`, and a municipality-centroid fallback may
still be `medium` when administrative identity is deterministic but spatially
coarse.

## Traceability Rules

The contract should preserve enough text to replay or replace the geocoder later
without re-scraping:

- normalization preserves source-backed address fragments and their provenance
- enrichment copies the normalized `geocoding_query_text` into the geocoding
  output for auditability
- enrichment stores the final resolved address text separately from the input
  query text so operators can compare requested and resolved forms
- unresolved or ambiguous cases must retain the input text even when no
  coordinates are emitted

## Artifact And Versioning Impact

`TASK-041` is a design-only task, so it should not change the active runtime
contracts by itself. The approved versioning implications are:

- `TASK-042` should bump the enrichment contract when the first geocoding fields
  land in `EnrichedLocationFeatures`
- `TASK-042` should also bump the normalization contract only if new normalized
  geocoding input fields such as `geocoding_query_text`, `house_number`, or
  `address_text` are added to `NormalizedLocation`
- modeling should not bump until a later implementation task explicitly
  promotes stable geocoding outputs into `ModelingFeatureSet`

Artifact implications once implemented:

- normalized artifacts must preserve the replayable geocoding input text and its
  provenance, not the geocoding result
- enriched artifacts must preserve both the normalized geocoding inputs and the
  resolved geocoding outputs with explicit precision and confidence fields
- municipality centroid coordinates must remain distinguishable from
  street-level or address-level coordinates through `location_precision` and
  `geocoding_is_fallback`, not through undocumented interpretation
