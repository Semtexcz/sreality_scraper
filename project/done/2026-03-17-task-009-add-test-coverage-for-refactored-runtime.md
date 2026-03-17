---
task: TASK-009
status: "done"
priority: P1
type: test
---

# Add regression-safe test coverage for the refactored runtime

Task: TASK-009
Status: done
Priority: P1
Type: test
Author:
Created: 2026-03-17
Related: TASK-002, TASK-005, TASK-006, TASK-007, TASK-008

## Problem

The refactored runtime will introduce new services, storage adapters, and a Typer CLI.
Without a focused regression test suite, future changes will be difficult to validate
and the refactor will remain fragile.

## Definition of Done

- [x] Add unit tests for scraper clients, parsers, storage adapters, and orchestration services.
- [x] Add CLI tests for Typer commands, argument validation, and bounded runtime options.
- [x] Add fixture-based tests for representative listing and detail pages.
- [x] Keep all tests deterministic and independent from live network services.
- [x] Verify both filesystem and MongoDB storage behavior where practical.
- [x] Ensure `poetry run pytest` passes in the refactored project.

## Notes

- Focus on behavior and public contracts rather than private implementation details.
- Mock network and persistence edges where needed to keep tests fast and stable.
- Include assertions that prove persisted records remain raw and unmodified.
