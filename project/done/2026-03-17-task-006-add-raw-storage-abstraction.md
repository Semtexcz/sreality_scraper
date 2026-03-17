---
task: TASK-006
status: "done"
priority: P1
type: feature
---

# Add a storage abstraction for raw scraper outputs

Task: TASK-006
Status: done
Priority: P1
Type: feature
Author:
Created: 2026-03-17
Related: TASK-004, TASK-005, TASK-007, TASK-008, TASK-009

## Problem

The project has not yet decided whether raw scraper outputs should be stored in
MongoDB or on the filesystem. Without a storage abstraction, that decision leaks into
the scraper runtime and forces persistence choices into unrelated parts of the code.

## Definition of Done

- [x] Define a storage interface for persisting raw listing records and optional raw page snapshots.
- [x] Implement a filesystem storage adapter.
- [x] Implement a MongoDB storage adapter.
- [x] Make storage backend selection configurable without changing scraper orchestration code.
- [x] Document operational tradeoffs for both storage backends.
- [x] Ensure stored records remain raw and are not enriched or normalized before persistence.

## Notes

- The scraper should depend on a storage abstraction, not on MongoDB-specific APIs.
- Storage adapters should own serialization and backend-specific write details.
- Keep record identity and idempotency concerns explicit rather than implicit.
