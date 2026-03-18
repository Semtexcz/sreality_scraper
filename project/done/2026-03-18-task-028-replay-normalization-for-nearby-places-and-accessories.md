---
task: TASK-028
status: "done"
priority: P2
type: docs
---

# Replay normalization for nearby places and accessories

Task: TASK-028
Status: done
Priority: P2
Type: docs
Author:
Created: 2026-03-18
Related: TASK-024, TASK-025, TASK-026, TASK-027

## Problem

Adding new normalized typed fields for nearby places and accessories will change
the canonical normalization output contract and persisted filesystem artifacts.
The project needs an explicit follow-up task that captures replay, validation,
and documentation work so the schema evolution remains visible and reproducible.

## Definition of Done

- [x] Replay normalization for representative persisted raw snapshots after the
      new fields are implemented.
- [x] Validate the updated normalized JSON artifacts against the intended schema
      and traceability expectations.
- [x] Update contract documentation, operator workflow notes, and any artifact
      examples that reference normalized outputs.
- [x] Review whether downstream enrichment or modeling stages should consume the
      new typed fields immediately or defer that work to later tasks.
- [x] Record any required migration notes in the changelog and release notes.

## Notes

- This task should happen only after the normalization contract and parser work
  are complete.
- Keep the replay scope explicit so reviewers can compare before and after
  artifacts deterministically.
