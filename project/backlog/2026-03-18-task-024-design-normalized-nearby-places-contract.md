---
task: TASK-024
status: "backlog"
priority: P1
type: design
---

# Design normalized nearby places contract

Task: TASK-024
Status: backlog
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

- [ ] Define a typed normalized contract for nearby places that can represent at
      least `category`, `name`, `distance_m`, and the original `source_text`.
- [ ] Decide whether nearby places should live in a dedicated top-level
      sub-contract or under the existing location grouping.
- [ ] Document how the typed field coexists with or replaces the current
      source-specific overflow keys.
- [ ] Define the parser provenance and fallback strategy for malformed values or
      future source drift.
- [ ] Identify any normalization contract version bump required by the new field.

## Notes

- Data analysis across current normalized snapshots found 9,279 nearby-place
  values matching the exact pattern `name(distance m)` with no unmatched
  examples in the inspected dataset.
- Categories currently appear as source-shaped keys such as `Bus MHD:`,
  `Metro:`, `Škola:`, `Školka:`, `Restaurace:`, `Pošta:`, and others.
- Preserve traceability so operators can still inspect the original raw text.
