---
task: TASK-024
status: "done"
priority: P1
type: design
---

# Design normalized nearby places contract

Task: TASK-024
Status: done
Priority: P1
Type: design
Author:
Created: 2026-03-18
Related: TASK-019

## Problem

Normalized records currently preserve nearby-place source fields such as
`Bus MHD:`, `Škola:`, or `Restaurace:` only under
`core_attributes.source_specific_attributes` as raw strings like
`Solidarita(91 m)`. The observed dataset is highly regular, so downstream
consumers should not need to re-parse those strings or depend on many
source-shaped keys to access place category, name, and walking-distance style
facts.

## Definition of Done

- [x] Define a typed normalized contract for nearby places that can represent at
      least `category`, `name`, `distance_m`, and the original `source_text`.
- [x] Decide whether nearby places should live in a dedicated top-level
      sub-contract or under the existing location grouping.
- [x] Document how the typed field coexists with or replaces the current
      source-specific overflow keys.
- [x] Define the parser provenance and fallback strategy for malformed values or
      future source drift.
- [x] Identify any normalization contract version bump required by the new field.

## Notes

- Data analysis across current normalized snapshots found 9,279 nearby-place
  values matching the exact pattern `name(distance m)` with no unmatched
  examples in the inspected dataset.
- Categories currently appear as source-shaped keys such as `Bus MHD:`,
  `Metro:`, `Škola:`, `Školka:`, `Restaurace:`, `Pošta:`, and others.
- Preserve traceability so operators can still inspect the original raw text.

## Design Decision

Nearby places should become part of the existing `location` grouping because the
data describes geographic context around the listing rather than core property
attributes or derived analytics. The normalization contract should therefore add a
new `nearby_places` collection to `NormalizedLocation` instead of introducing a new
top-level record section.

The collection should contain a typed `NormalizedNearbyPlace` sub-contract with the
following fields:

- `category: str`
- `name: str | None`
- `distance_m: int | None`
- `source_text: str`
- `source_key: str`

`category` is the stable normalized label used by downstream consumers, while
`source_key` preserves the original source-shaped attribute name such as
`Bus MHD:` or `Škola:`. `source_text` keeps the original raw value exactly as it
appeared in the source payload so operators can audit parser behavior. `name` and
`distance_m` remain optional to support partial parsing without dropping the raw
fact.

## Overflow And Compatibility Rules

Supported nearby-place keys should stop being duplicated in
`core_attributes.source_specific_attributes` once they are mapped into
`location.nearby_places`. The typed field becomes the canonical access path for
recognized nearby-place categories.

Unknown future source keys should remain in
`core_attributes.source_specific_attributes` unchanged. Recognized keys with
malformed values should still emit a `NormalizedNearbyPlace` entry with populated
`category`, `source_key`, and `source_text`, while `name` and `distance_m` stay
`None` when parsing fails. This preserves traceability without forcing downstream
consumers to depend on the overflow bag for known categories.

## Parser Provenance And Fallback

Nearby-place parsing should use a dedicated normalization parser implementation
versioned in code as `nearby-places-v1`. That parser version does not need a new
record-level metadata field because the record already carries
`normalization_version`, which versions the emitted contract as a whole.

The parser should treat the current `name(distance m)` shape as the primary
deterministic pattern. For recognized source keys:

- When the value matches the expected pattern, populate all typed fields.
- When only the category can be trusted, emit a partial typed entry and preserve
  the original `source_text`.
- When the source key is not part of the approved nearby-place mapping, leave the
  value in `source_specific_attributes` only.

This fallback keeps normalization resilient to source drift while avoiding hard
failures for the entire listing.

## Contract Version Impact

Adding `location.nearby_places` is an additive schema change to the canonical
normalized record. The follow-up implementation task should therefore bump the
normalization contract from `normalized-listing-v4` to `normalized-listing-v5` and
update tests and persisted artifact expectations accordingly.
