---
task: TASK-053
status: "done"
priority: P1
type: design
---

# Design a notebook analysis-dataset contract

Task: TASK-053
Status: done
Priority: P1
Type: design
Author:
Created: 2026-03-19
Related: TASK-015, TASK-039, TASK-046

## Problem

The exploratory notebook should analyze a stable tabular dataset rather than
flattening enriched or modeling artifacts ad hoc inside notebook cells. The
repository does not yet define the canonical notebook-facing projection,
required columns, deduplication rules, target fields, or the lineage metadata
needed to keep later training work aligned with exploratory findings.

## Definition of Done

- [x] Define the first supported notebook analysis-dataset contract derived from
      enriched or modeling artifacts only.
- [x] Specify the required columns, field ownership, and target semantics for
      `asking_price_czk` and `price_per_square_meter_czk`.
- [x] Define listing deduplication, snapshot selection, and data-quality
      inclusion rules required before notebook analysis begins.
- [x] Decide whether the dataset should be persisted as a new artifact family,
      a deterministic export workflow, or a notebook-local derived table.
- [x] Document lineage and versioning expectations so later training workflows
      can consume the same approved dataset semantics.

## Notes

- Prefer a thin deterministic projection over business logic duplicated in the
  notebook.
- Keep the contract explicit about geocoding precision and approximation
  signals so downstream spatial analysis can filter or weight records safely.
- The design should make it possible to implement notebook and training
  workflows without redefining feature semantics later.

## Design Decision

`TASK-053` approves a canonical analysis-dataset export contract for notebook
and later training workflows.

The first supported repository approach must:

1. materialize a versioned derived artifact through a deterministic export
   workflow rather than notebook-local flattening
2. start from `ModelingInputRecord` for stable feature columns
3. copy selected enrichment-owned resolved-coordinate and geocoding fields
   without redefining their semantics
4. emit one row per deduplicated `listing_id`, using the latest supported
   captured snapshot as the default cross-sectional view
5. enforce mandatory base-row validity for price and area targets while leaving
   notebook-specific map and modeling filters explicit downstream
6. preserve enough lineage metadata for later notebook and training workflows to
   replay the same semantics from persisted artifacts

## Contract And Artifact Outcome

The approved repository-level contract is documented in
`docs/ANALYSIS_DATASET_CONTRACT.md`.

That design defines:

- the row grain and deduplication policy
- required columns and field ownership
- target semantics for `asking_price_czk` and
  `price_per_square_meter_czk`
- mandatory inclusion and exclusion rules before notebook analysis begins
- the decision to persist a versioned analysis-dataset artifact family via the
  later `TASK-054` export workflow
