---
task: TASK-050
status: "done"
priority: P1
type: design
---

# Design a source-backed raw-coordinate contract

Task: TASK-050
Status: done
Priority: P1
Type: design
Author:
Created: 2026-03-19
Related: TASK-012, TASK-048, TASK-049

## Problem

The current implementation can recover precise listing coordinates only when the
raw dataset preserves full detail HTML in `raw_page_snapshot`. Most existing raw
records do not persist that snapshot, so replay alone cannot recover the
source-backed GPS points already exposed by Sreality detail pages. The project
needs an approved raw-contract design for carrying replay-safe source-backed
coordinates directly in `source_payload` without requiring full HTML retention.

## Definition of Done

- [x] Define the canonical scraper-owned raw fields for source-backed detail
      coordinates extracted from the embedded locality payload.
- [x] Specify whether the raw contract should store only latitude/longitude or
      also keep source provenance and source precision hints alongside them.
- [x] Define the precedence between raw embedded coordinates and
      `raw_page_snapshot`-based recovery so downstream normalization remains
      deterministic during migration.
- [x] Document any backward-compatibility and artifact-versioning impacts on raw
      storage, normalization, and replay workflows.
- [x] Document the parser boundary explicitly so map-link query parameters and
      weaker presentation hints do not enter the raw contract implicitly.

## Notes

- Favor storing only replay-safe fields that are deterministic direct source
  facts rather than presentation-derived guesses.
- Keep the design compatible with older raw artifacts that may still omit the
  new coordinate fields.
- The goal is to reduce dependence on storing full detail HTML for future raw
  captures, not to break existing snapshot-based replay.

## Design Decision

Source-backed detail coordinates should become an explicit scraper-owned raw
sub-contract stored inside `RawListingRecord.source_payload`, while
`raw_page_snapshot` remains an optional migration fallback for older captures
and markup-debug workflows.

This task does not move final coordinate ownership out of enrichment. It
approves only the upstream raw boundary needed so future scraper runs can
persist replay-safe source facts without retaining full detail HTML.

The key split is:

- scraper owns capture of deterministic source facts exposed by Sreality detail
  pages
- normalization owns reshaping those raw facts into the normalized
  `source_coordinate_*` fields approved by `TASK-048`
- enrichment still owns the final winning coordinate and all fallback quality
  semantics

## Proposed Raw Contract Ownership

### Raw Listing Record

The canonical raw contract should remain `RawListingRecord`, but
`source_payload` should gain one explicit nested object for replay-safe detail
coordinates:

- `source_payload["source_coordinates"]`

Approved fields inside that object:

- `latitude: float`
- `longitude: float`
- `source: str`
- `precision: str | None`

Approved vocabulary for this task:

- `source = "detail_locality_payload"`
- `precision = "listing"` or `None`

The object should be omitted entirely when the scraper cannot recover both
numeric coordinate values from the approved source path.

This is intentionally narrow:

- `latitude` and `longitude` are the canonical required facts because they are
  the replay-safe values needed by downstream normalization
- `source` is also approved for storage because migration and future parser
  changes need explicit provenance when multiple raw extraction paths may exist
- `precision` is approved because the embedded locality payload already carries
  enough semantics to distinguish listing-level source coordinates from weaker
  future candidates without forcing normalization to infer that distinction
  later

No additional raw confidence, fallback, or geocoding-match fields are approved.
Those remain enrichment concerns because they describe downstream coordinate
selection rather than direct source capture.

### Source Metadata

`RawSourceMetadata` should remain unchanged by this task.

Parser versioning and capture context already belong in `source_metadata`.
Coordinate provenance that explains one payload fragment belongs with the raw
payload fragment itself, so it should not be duplicated into metadata-level
fields.

## Deterministic Precedence During Migration

Normalization must use one explicit precedence ladder while both old and new raw
artifacts coexist:

1. `source_payload["source_coordinates"]` when the object exists and contains
   valid numeric `latitude` and `longitude`
2. `raw_page_snapshot` replay of the approved embedded locality payload for
   older artifacts that do not yet persist `source_coordinates`
3. no source-backed coordinate

This precedence is deterministic and intentionally favors the structured raw
payload over reparsing HTML because:

- the new raw field is the approved scraper-owned contract for future captures
- replay should not depend on HTML retention when an equivalent structured raw
  fact is already present
- older artifacts remain compatible until `TASK-051` or later backfills them

When both the new raw object and `raw_page_snapshot` are present, normalization
must trust the structured raw object and must not attempt to merge or arbitrate
between the two values silently. Any future validation or mismatch detection can
be added separately, but it is not part of this contract.

## Parser Boundary

The raw-coordinate parser boundary is explicitly limited to the embedded
detail-page locality payload that is already available in the captured detail
HTML.

Approved for raw storage:

- numeric latitude/longitude read from the embedded locality object
- provenance `source = "detail_locality_payload"`
- precision hint `precision = "listing"` when the approved locality path is
  used

Not approved for raw storage in this task:

- map-link query parameters
- third-party map script state
- nearby-place coordinates
- inferred coordinates reconstructed from address text
- enrichment-side fallback coordinates such as district or municipality
  centroids
- undocumented copies of the same facts at multiple payload paths

This keeps the raw contract source-backed and deterministic. Weaker
presentation-derived hints must not enter `source_payload["source_coordinates"]`
implicitly.

## Backward Compatibility And Versioning Impact

`TASK-050` is design-only and does not change runtime behavior by itself. The
approved implementation impact for `TASK-051` is:

- `RawListingRecord` remains the canonical scraper contract, but the serialized
  payload shape will expand with an optional `source_coordinates` object inside
  `source_payload`
- the raw contract version should bump from `raw-listing-record-v1` to
  `raw-listing-record-v2` when that field starts being emitted
- raw persistence adapters must preserve the nested object verbatim when
  present
- normalization should continue accepting `raw-listing-record-v1` artifacts
  that omit the field and should use the migration precedence defined above
- normalization and enrichment contract versions do not need to change for this
  raw-contract task alone because `TASK-049` already introduced the downstream
  normalized and enriched coordinate fields

Replay implications once implemented:

- future raw captures can preserve source-backed listing coordinates without
  storing full `raw_page_snapshot`
- older raw captures remain replayable through snapshot parsing when snapshots
  exist
- artifacts that omit both `source_coordinates` and `raw_page_snapshot` will
  continue to produce no source-backed coordinate, which stays explicit and
  backward-compatible
- `raw_page_snapshot` remains allowed for diagnostics, parser validation, and
  legacy replay, but it is no longer the preferred carrier for approved
  source-backed coordinates

## Implementation Guidance For TASK-051

`TASK-051` should:

- extract the approved locality payload coordinates during scraping
- persist them under `source_payload["source_coordinates"]`
- keep `raw_page_snapshot` optional and independent of coordinate persistence
- update normalization so it reads the new raw object before falling back to
  `raw_page_snapshot`
- add regression coverage for new-artifact precedence, old-artifact fallback,
  and coordinate-missing records
