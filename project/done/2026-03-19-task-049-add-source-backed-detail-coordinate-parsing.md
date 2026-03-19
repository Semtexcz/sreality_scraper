---
task: TASK-049
status: "done"
priority: P1
type: feature
---

# Add source-backed detail coordinate parsing

Task: TASK-049
Status: done
Priority: P1
Type: feature
Author:
Created: 2026-03-19
Related: TASK-042, TASK-048

## Problem

Live Sreality detail HTML for listing `78467916` already exposes
`locality.latitude=50.0577347` and `locality.longitude=14.3723456`, while the
current enrichment output falls back to an approximate street-level projection.
The scraper therefore misses available source-backed coordinates and downgrades
location precision unnecessarily.

## Definition of Done

- [x] Parse source-backed latitude and longitude from the embedded detail-page
      HTML payload for listings that expose locality coordinates.
- [x] Persist the extracted coordinate fields and provenance in the normalized
      location contract.
- [x] Update enrichment so source-backed detail coordinates take precedence over
      deterministic fallback geocoding when present.
- [x] Preserve explicit precision and confidence semantics so downstream outputs
      clearly distinguish source-backed GPS from projected fallback coordinates.
- [x] Add regression coverage for listings with source-backed coordinates and
      listings that still require fallback geocoding.
- [x] Refresh affected documentation and canonical artifact versions so replayed
      outputs reflect the new coordinate source order.

## Notes

- Prefer parsing the embedded locality JSON object over deriving coordinates
  from presentation-only links.
- Keep the implementation resilient to missing coordinates and unchanged detail
  pages that expose no locality geometry.
