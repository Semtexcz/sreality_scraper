---
task: TASK-019
status: "done"
priority: P1
type: feature
---

# Broaden normalized field coverage from the detail payload

Task: TASK-019
Status: done
Priority: P1
Type: feature
Author:
Created: 2026-03-18
Related: TASK-013, TASK-015, TASK-020

## Problem

The current normalization contract only exposes title, price, building, and basic
location fields even though the raw `all-czechia` dataset already contains richer
detail-page attributes at high coverage. Across the current 477 raw JSON snapshots,
`Plocha:`, `Vlastnictví:`, `Vloženo:`, and `Upraveno:` appear in 472 records,
`Příslušenství:` appears in 457 records, `ID zakázky:` appears in 448 records, and
`Energetická náročnost:` appears in 439 records. Downstream stages currently have to
ignore this stable source data or recover it indirectly from raw overflow fields.

## Definition of Done

- [ ] Expand `NormalizedListingRecord` with typed field groups for floor-area data,
      ownership, listing lifecycle dates, and source listing identifiers that are
      present in the raw detail payload.
- [ ] Parse raw area strings from `Plocha:` into explicit stable fields while
      preserving the original text when a fragment cannot be decomposed fully.
- [ ] Normalize `Vlastnictví:`, `ID zakázky:`, `Vloženo:`, and `Upraveno:` into
      dedicated typed fields instead of leaving them only in
      `source_specific_attributes`.
- [ ] Keep all newly supported fields deterministic and sourced only from the raw
      scraper payload without introducing derived analytics.
- [ ] Preserve unmapped or partially parsed source fragments for traceability.
- [ ] Add focused tests that cover representative detail payload variants drawn from
      `data/raw/all-czechia`, including missing optional values.

## Notes

- Favor explicit sub-contracts over a flat record with many optional fields.
- Treat parsed numeric values and dates as normalization, not enrichment, only when
  they are direct reshaping of raw source text.
- Do not introduce price-per-square-meter or similar derived business features here.
