---
task: TASK-022
status: "todo"
priority: P1
type: feature
---

# Add typed price, building, and energy normalization

Task: TASK-022
Status: todo
Priority: P1
Type: feature
Author:
Created: 2026-03-18
Related: TASK-013, TASK-019, TASK-020, TASK-021

## Problem

The current normalization contract still preserves several important source facts as
raw text only. Price remains available only as `amount_text`, building facts are
collapsed into the overloaded `building.condition` field, and energy-efficiency
details are kept only as one source string. These values come directly from the raw
detail payload and can be parsed deterministically without crossing into derived
analytics. Leaving them unstructured makes downstream use harder and forces later
stages to re-parse already normalized data.

## Definition of Done

- [ ] Expand the normalized price contract to preserve raw source text and expose
      typed monetary fields suitable for Czech listing prices.
- [ ] Parse price text deterministically from the raw payload without using floating
      point representation for whole-currency amounts.
- [ ] Replace the overloaded `building.condition` storage with explicit typed fields
      for source-backed building facts such as physical condition, floor position,
      floor count, and other directly stated structural attributes where parsing is
      reliable.
- [ ] Preserve the original building source text or unmapped fragments whenever a
      source value cannot be decomposed fully.
- [ ] Expand the normalized energy-efficiency contract to expose structured fields
      such as the efficiency grade and consumption value when present in the raw
      payload.
- [ ] Keep every new normalized field deterministic and sourced only from raw
      scraper output rather than inferred business semantics.
- [ ] Add focused tests covering representative real snapshots from
      `data/raw/all-czechia`, including missing optional values and partially
      parseable source strings.

## Notes

- Keep raw source text alongside parsed fields for traceability.
- Prefer `int` over `float` for whole-currency price amounts.
- Do not compute derived metrics such as `price_per_sqm`, `is_top_floor`, or
  energy buckets in normalization.
