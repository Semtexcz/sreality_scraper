---
task: TASK-048
status: "done"
priority: P1
type: design
---

# Design a source-backed detail-coordinate contract

Task: TASK-048
Status: done
Priority: P1
Type: design
Author:
Created: 2026-03-19
Related: TASK-041, TASK-042

## Problem

The Sreality detail page for at least some listings embeds precise listing
coordinates in the HTML payload under the page-local locality object. The
current pipeline does not define how source-backed coordinates should be
captured, traced, and propagated relative to the existing deterministic
fallback geocoding ladder, so accurate coordinates are currently discarded and
replaced by less precise derived estimates.

## Definition of Done

- [x] Define the canonical normalized fields for source-backed detail-page
      coordinates, including provenance and any source precision metadata that
      can be recovered reliably.
- [x] Specify how enrichment should prioritize source-backed coordinates versus
      deterministic fallback geocoding when both are available.
- [x] Define how coordinate provenance, precision, and confidence should be
      exposed so downstream consumers can distinguish source-backed GPS from
      projected or centroid-based fallback results.
- [x] Document the parsing boundary for embedded HTML JSON versus weaker map-link
      extraction so scraper behavior remains explicit and maintainable.
- [x] Document artifact and versioning impacts across normalization,
      enrichment, and any affected modeling outputs before implementation.

## Notes

- Favor the embedded locality payload as the primary source when available.
- Treat map-link coordinates as a secondary fallback only if they are proven to
  be stable and semantically equivalent to the locality coordinates.
- Keep source-backed coordinate extraction deterministic and replayable from
  persisted raw detail HTML.

## Design Decision

Source-backed coordinates embedded in the Sreality detail HTML belong in
normalization as direct source facts, while enrichment remains the canonical
owner of the final coordinate chosen for downstream analytics.

This keeps the existing stage split intact:

- normalization may reshape latitude/longitude that already exist in the
  persisted detail HTML because they are still source-backed facts
- enrichment still decides which coordinate wins, how precise it is, whether it
  is fallback-derived, and how it should be exposed to modeling and analytics

The approved design therefore extends `NormalizedLocation` with one explicit
source-coordinate group and extends the existing enrichment geocoding contract
so it can represent direct source-backed listing points in addition to derived
fallback points.

## Proposed Contract Ownership

### Normalization

`NormalizedLocation` should stay the canonical boundary for source-backed
location facts and add these optional fields:

- `source_coordinate_latitude: float | None`
- `source_coordinate_longitude: float | None`
- `source_coordinate_source: str | None`
- `source_coordinate_precision: str | None`

Approved vocabulary:

- `source_coordinate_source`: `detail_locality_payload`
- `source_coordinate_precision`: `listing`, `unknown`

The intent is conservative:

- `source_coordinate_latitude` and `source_coordinate_longitude` are populated
  only when the embedded detail-page locality object exposes both numeric values
  deterministically
- `source_coordinate_source` records which raw source fragment produced the
  point; `TASK-048` approves only `detail_locality_payload`
- `source_coordinate_precision` records the strongest semantics that can be
  asserted from the source itself; use `listing` only for the approved locality
  payload path and leave the field `None` when the parser cannot prove the
  source semantics cleanly

Normalization must not assign geocoding confidence, fallback status, or any
reference-backed interpretation to these fields. They remain direct reshaped
source facts.

### Enrichment

Enrichment should continue to own the final coordinate contract inside
`EnrichedLocationFeatures`, but its existing fields must explicitly support
source-backed points.

The approved priority order for the final coordinate is:

1. `NormalizedLocation.source_coordinate_*` from the approved
   `detail_locality_payload`
2. deterministic address geocoding
3. deterministic street projection
4. district reference fallback
5. municipality centroid fallback
6. unresolved

When a normalized source-backed coordinate is present and valid, enrichment must
promote it into the final output by:

- setting `latitude` and `longitude` from the normalized source coordinate
- extending `location_precision` with the new value `listing`
- setting `geocoding_source` to `detail_locality_payload`
- setting `geocoding_match_strategy` to `source_detail_coordinate`
- setting `geocoding_confidence` to `high`
- setting `geocoding_fallback_level` to `none`
- setting `geocoding_is_fallback` to `False`

This design keeps the current enriched field names for compatibility. Even
though `geocoding_source` historically described derived matches, it is now the
canonical field for the final coordinate origin, including direct source-backed
detail points.

### Modeling

`TASK-048` does not require new modeling fields. Existing modeling consumers can
continue to read final coordinates only from enrichment once implementation
lands.

The only approved downstream semantic expansion is that future consumers of
`location_precision` must treat `listing` as a higher-fidelity category than
`address`, `street`, `district`, or `municipality`. No new modeling-only
traceability fields are required by this design.

## Provenance, Precision, And Confidence Semantics

The contract must let downstream consumers distinguish source-backed listing
points from projected or centroid-based fallbacks without reading free-text
notes.

Required interpretation:

- `location_precision = listing` means the final coordinate came directly from
  the source-backed detail payload rather than from enrichment-side geocoding or
  reference fallback
- `geocoding_source = detail_locality_payload` identifies the winning source as
  embedded detail HTML
- `geocoding_match_strategy = source_detail_coordinate` identifies the
  deterministic rule path that selected the final point
- `geocoding_is_fallback = False` distinguishes source-backed and direct
  high-priority outcomes from street, district, or municipality fallback paths
- `geocoding_confidence = high` describes confidence in the deterministic parser
  and source-backed provenance, not a promise about parcel-level legal accuracy

Confidence and precision must remain separate. A source-backed point may still
need a conservative precision label in the future if Sreality changes its map
semantics, but it should not be collapsed into the same categories used for
projected street or centroid fallbacks.

## Parsing Boundary

The approved parser boundary is intentionally narrow.

`TASK-049` may extract source-backed coordinates only from the embedded
detail-page HTML JSON that contains the page-local locality object and is
already recoverable from the persisted detail markup without browser execution.

Explicitly approved:

- parsing numeric latitude/longitude from the embedded locality object inside
  the persisted detail HTML
- recording that path as `source_coordinate_source = detail_locality_payload`

Explicitly not approved in this task:

- parsing coordinates from outbound map links or query parameters by default
- inferring listing coordinates from nearby-place points
- extracting coordinates from third-party script payloads, remote API calls, or
  browser-executed map state
- silently mixing locality-payload coordinates with weaker map-link hints into
  one undocumented field

Map-link extraction remains a possible future fallback only if a later task
proves that the link is stable, replayable from persisted raw artifacts, and
semantically equivalent to the approved locality payload. If that ever lands, it
must use the same normalized fields with a different explicit
`source_coordinate_source` value and lower priority than
`detail_locality_payload`.

## Artifact And Versioning Impact

`TASK-048` is design-only, so it does not change the active runtime contracts by
itself. The approved implementation impact is:

- `TASK-049` should bump the normalization contract because
  `NormalizedLocation` will gain new `source_coordinate_*` fields
- `TASK-049` should bump the enrichment contract because
  `EnrichedLocationFeatures.location_precision` will gain `listing` and the
  final coordinate-priority rules will change
- modeling does not need a version bump unless a later task explicitly promotes
  `location_precision`, source-backed flags, or other new location helpers into
  `ModelingFeatureSet`

Artifact implications once implemented:

- raw artifacts used for coordinate extraction must preserve the replayable
  detail HTML fragment or equivalent raw locality JSON needed to reproduce the
  normalized source-coordinate fields deterministically
- normalized artifacts become the canonical persisted boundary for
  source-backed detail coordinates and must preserve their explicit provenance
- enriched artifacts remain the canonical persisted boundary for the final
  winning coordinate, including whether it came from the source-backed detail
  payload or from deterministic fallback geocoding
- downstream spatial features such as grid cells, urban-center distances, and
  later price-surface workflows must derive from the enriched winning
  coordinate, not by re-reading normalized source-coordinate fields directly
