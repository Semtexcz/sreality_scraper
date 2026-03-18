---
task: TASK-030
status: "done"
priority: P2
type: feature
---

# Add building layout and condition enrichment features

Task: TASK-030
Status: done
Priority: P2
Type: feature
Author:
Created: 2026-03-18
Related: TASK-022, TASK-023, TASK-029

## Problem

Normalized records now expose stable building facts such as floor position, total
floor count, material, and physical condition, but enrichment currently converts
only a small subset of that information into downstream-friendly semantics. That
leaves modeling consumers to interpret important building context themselves.

## Definition of Done

- [ ] Extend enrichment with deterministic building-derived features computed only
      from `core_attributes.building`.
- [ ] Add explicit semantics for at least ground-floor, upper-floor, and relative
      floor-position interpretation where the source values make those features
      reliable.
- [ ] Introduce coarse, documented buckets for building material and physical
      condition that preserve optionality for unknown or unsupported values.
- [ ] Keep every new feature nullable when normalized building fields are missing,
      malformed, or insufficient for an unambiguous derivation.
- [ ] Add focused tests that cover common building combinations observed in the
      normalized dataset, including low-rise and high-rise buildings.

## Notes

- Avoid overfitting to current Czech labels; prefer small stable buckets with
  traceable mapping rules.
- If a feature depends on both `floor_position` and `total_floor_count`, do not
  infer it when either field is absent.
- Review whether any new building features should also be propagated into
  `ModelingFeatureSet` as part of the same implementation or a direct follow-up.
