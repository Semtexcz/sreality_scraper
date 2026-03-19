---
task: TASK-051
status: "todo"
priority: P1
type: feature
---

# Add source-backed raw-coordinate parsing

Task: TASK-051
Status: todo
Priority: P1
Type: feature
Author:
Created: 2026-03-19
Related: TASK-050, TASK-049

## Problem

Future raw captures should preserve source-backed listing coordinates even when
full detail HTML snapshots are not stored. At the moment the scraper emits only
the normalized detail `dt/dd` payload and optional full HTML snapshots, which
means precise coordinates are lost for the dominant raw dataset path.

## Definition of Done

- [ ] Parse source-backed latitude and longitude from the embedded detail-page
      locality payload during scraping and persist them directly in the raw
      listing contract.
- [ ] Preserve any approved raw provenance fields defined by `TASK-050` so the
      raw contract remains explicit about where the coordinate came from.
- [ ] Update raw-storage and normalization flows so normalization can consume
      the raw coordinate fields without requiring `raw_page_snapshot`.
- [ ] Keep backward compatibility for older raw artifacts that still rely on
      snapshot-based coordinate recovery.
- [ ] Add regression coverage for scraper parsing, raw persistence, and
      normalization behavior with and without stored HTML snapshots.
- [ ] Refresh affected documentation and canonical artifact versions so future
      operator workflows know rescrape can recover GPS without storing full
      detail HTML.

## Notes

- Prefer the same embedded locality JSON already approved in `TASK-049`.
- Do not silently expand the scraper contract to map-link or browser-executed
  coordinate sources.
- The implementation should improve future raw captures; older raw data without
  snapshots will still require re-scraping if they were already stored without
  the new fields.
