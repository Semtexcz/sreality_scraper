---
task: TASK-048
status: "todo"
priority: P1
type: design
---

# Design a source-backed detail-coordinate contract

Task: TASK-048
Status: todo
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

- [ ] Define the canonical normalized fields for source-backed detail-page
      coordinates, including provenance and any source precision metadata that
      can be recovered reliably.
- [ ] Specify how enrichment should prioritize source-backed coordinates versus
      deterministic fallback geocoding when both are available.
- [ ] Define how coordinate provenance, precision, and confidence should be
      exposed so downstream consumers can distinguish source-backed GPS from
      projected or centroid-based fallback results.
- [ ] Document the parsing boundary for embedded HTML JSON versus weaker map-link
      extraction so scraper behavior remains explicit and maintainable.
- [ ] Document artifact and versioning impacts across normalization,
      enrichment, and any affected modeling outputs before implementation.

## Notes

- Favor the embedded locality payload as the primary source when available.
- Treat map-link coordinates as a secondary fallback only if they are proven to
  be stable and semantically equivalent to the locality coordinates.
- Keep source-backed coordinate extraction deterministic and replayable from
  persisted raw detail HTML.
