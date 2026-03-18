# Enrichment Task Sequence

This document records the recommended implementation order for the current
enrichment and location-intelligence backlog. The goal is to deliver the highest
value features first while avoiding rework across stage boundaries and contract
versions.

The sequence covers `TASK-029` through `TASK-039`. Although the user-facing
backlog discussion often referred to "ten tasks", there are currently eleven
active backlog items in this slice because the operator-facing enrichment workflow
is tracked separately as `TASK-034`.

## Recommended Order

1. `TASK-035`: design location intelligence contract and reference mapping
2. `TASK-036`: add reference-backed municipality and administrative location features
3. `TASK-037`: add coordinate and macro-distance location enrichment
4. `TASK-029`: add area-based enrichment features from normalized area fields
5. `TASK-030`: add building layout and condition enrichment features
6. `TASK-031`: add accessory and outdoor space enrichment features
7. `TASK-032`: add nearby-place accessibility enrichment features
8. `TASK-033`: add listing freshness and lifecycle enrichment features
9. `TASK-038`: add metropolitan district and spatial cell location features
10. `TASK-039`: propagate location intelligence into modeling inputs
11. `TASK-034`: expose enrichment as an operator workflow

## Why This Order

### Phase 1: Location foundation

`TASK-035`, `TASK-036`, and `TASK-037` come first because location is expected to
be the strongest price driver and because later location features depend on
stable reference matching and coordinate provenance. These tasks establish:

- the contract split between normalization, enrichment, and modeling
- the deterministic join strategy for `data/souradnice.csv`,
  `data/OkresniMesta.csv`, and `data/ObceSRozsirenouPusobnosti.csv`
- the first spatial baseline via administrative identifiers, coordinates, and
  macro-distance metrics

Without this foundation, metropolitan logic and model-facing location features
would be built on unstable assumptions.

### Phase 2: General enrichment expansion

`TASK-029` through `TASK-033` expand the enrichment contract from already
normalized fields that have strong coverage in the current dataset. This phase is
ordered by expected value and implementation risk:

- `TASK-029` removes title-regex dependence for area-derived pricing features
- `TASK-030` adds building semantics from typed building fields
- `TASK-031` adds accessory and outdoor-space features from typed accessories
- `TASK-032` adds amenity and accessibility signals from `nearby_places`
- `TASK-033` adds deterministic lifecycle freshness features

These tasks do not require the full modeling boundary to be finalized, so they
can mature the enrichment contract first.

### Phase 3: Urban refinement and modeling handoff

`TASK-038` is intentionally later because metropolitan bucketing is valuable but
more specialized. It should build on the already approved municipality and
coordinate approach instead of introducing city-specific rules too early.

`TASK-039` should follow once the approved enrichment-side location feature set is
stable enough to expose through `ModelingFeatureSet`. This reduces avoidable
modeling contract churn.

### Phase 4: Operator workflow

`TASK-034` is last because the public enrichment workflow should replay a mature
feature set rather than a rapidly changing intermediate schema. Implementing it
after the core feature work also makes the CLI and artifact documentation more
stable.

## Dependency Notes

- `TASK-035` blocks `TASK-036`, `TASK-037`, and strongly informs `TASK-038`.
- `TASK-036` should precede `TASK-037` because administrative matching anchors the
  coordinate and distance layer.
- `TASK-037` should precede `TASK-038` because metropolitan bucketing benefits
  from an already approved coordinate baseline.
- `TASK-039` should follow `TASK-032`, `TASK-036`, `TASK-037`, and `TASK-038`
  because it packages their outputs for model consumption.
- `TASK-034` should be implemented after the contract-impacting feature tasks so
  the workflow does not need repeated migration changes.

## Practical Delivery Plan

If implementation needs to be split into smaller milestones, use these batches:

1. Foundation batch:
   `TASK-035`, `TASK-036`, `TASK-037`
2. General enrichment batch:
   `TASK-029`, `TASK-030`, `TASK-031`, `TASK-032`, `TASK-033`
3. Urban and modeling batch:
   `TASK-038`, `TASK-039`
4. Workflow batch:
   `TASK-034`

This batching gives the project a strong first usable location baseline before
the operator-facing enrichment replay is exposed.
