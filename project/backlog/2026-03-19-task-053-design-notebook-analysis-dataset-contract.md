---
task: TASK-053
status: "backlog"
priority: P1
type: design
---

# Design a notebook analysis-dataset contract

Task: TASK-053
Status: backlog
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

- [ ] Define the first supported notebook analysis-dataset contract derived from
      enriched or modeling artifacts only.
- [ ] Specify the required columns, field ownership, and target semantics for
      `asking_price_czk` and `price_per_square_meter_czk`.
- [ ] Define listing deduplication, snapshot selection, and data-quality
      inclusion rules required before notebook analysis begins.
- [ ] Decide whether the dataset should be persisted as a new artifact family,
      a deterministic export workflow, or a notebook-local derived table.
- [ ] Document lineage and versioning expectations so later training workflows
      can consume the same approved dataset semantics.

## Notes

- Prefer a thin deterministic projection over business logic duplicated in the
  notebook.
- Keep the contract explicit about geocoding precision and approximation
  signals so downstream spatial analysis can filter or weight records safely.
- The design should make it possible to implement notebook and training
  workflows without redefining feature semantics later.
