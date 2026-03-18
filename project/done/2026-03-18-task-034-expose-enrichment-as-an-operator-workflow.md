---
task: TASK-034
status: "done"
priority: P1
type: feature
---

# Expose enrichment as an operator workflow

Task: TASK-034
Status: done
Priority: P1
Type: feature
Author:
Created: 2026-03-18
Related: TASK-021, TASK-023, TASK-029, TASK-032, TASK-033, TASK-036, TASK-037, TASK-038

## Problem

The roadmap now treats normalization as a supported operator-facing replay
workflow, but enrichment remains an internal component only. Once the derived
feature set grows, operators need an explicit way to replay normalized artifacts
into canonical enriched outputs without going through raw scraping or the full
linear pipeline.

## Definition of Done

- [x] Add a supported CLI or workflow entrypoint that reads normalized filesystem
      artifacts and emits enriched artifacts in a deterministic layout.
- [x] Keep the workflow scoped to enrichment-stage inputs and outputs only, without
      weakening the raw-only acquisition path.
- [x] Add integration-style coverage that validates representative normalized
      snapshots are replayed into enriched artifacts successfully.
- [x] Document the workflow usage, artifact location, and traceability guarantees
      for operators.
- [x] Update roadmap or developer-facing documentation so enrichment is clearly
      described as a supported stage entrypoint.

## Notes

- Reuse the normalization workflow structure where it improves consistency, but do
  not assume the same persistence decisions without documenting them.
- Decide explicitly whether enriched artifacts become first-class persisted outputs
  or remain workflow-local files.
- This task should include any necessary contract, changelog, or migration updates
  if the enriched schema changes beforehand.
- The operator-facing workflow should be able to replay future location
  intelligence fields so reference-backed location enrichment can be validated on
  persisted normalized artifacts, not just in unit tests.
