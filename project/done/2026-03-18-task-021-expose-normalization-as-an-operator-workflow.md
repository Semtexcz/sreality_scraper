---
task: TASK-021
status: "done"
priority: P2
type: feature
---

# Expose normalization as an operator workflow

Task: TASK-021
Status: done
Priority: P2
Type: feature
Author:
Created: 2026-03-18
Related: TASK-013, TASK-019, TASK-020, TASK-015

## Problem

Normalization exists only as an internal component in the linear in-process pipeline.
Operators can collect raw snapshots, but they cannot deliberately run normalization
against an existing raw dataset, inspect normalized outputs, or validate stage
handoffs on representative captured data. That keeps the stage difficult to use,
debug, and verify independently even though `data/raw/all-czechia` already provides
real-world inputs for an operator-facing workflow.

## Definition of Done

- [x] Add a supported user-facing entrypoint that runs normalization from persisted
      raw records without requiring enrichment or modeling execution.
- [x] Support normalization over filesystem-backed raw snapshots and document the
      expected input and output locations or stream format.
- [x] Define how operators select a raw source scope such as one listing, one run,
      or one region dataset.
- [x] Emit stable normalized outputs with explicit version metadata suitable for
      inspection, testing, and downstream reuse.
- [x] Add integration-style tests that execute the normalization workflow against
      representative raw fixtures derived from `data/raw/all-czechia`.
- [x] Update developer-facing documentation so the public normalization workflow,
      constraints, and traceability guarantees are clear.

## Notes

- Keep the existing raw-only acquisition workflow intact; this task adds a deliberate
  normalization entrypoint rather than replacing the scraper CLI.
- The initial operator workflow may target filesystem persistence only if MongoDB
  support would otherwise broaden the task too much.
