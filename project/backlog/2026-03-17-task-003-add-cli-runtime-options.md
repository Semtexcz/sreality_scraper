---
task: TASK-003
status: "backlog"
priority: P1
type: feature
---

# Define runtime options for the future Typer CLI

Task: TASK-003
Status: backlog
Priority: P1
Type: feature
Author:
Created: 2026-03-17
Related: TASK-004, TASK-007

## Problem

The scraper does not yet expose a coherent operator-facing command-line interface.
Runtime limits and selection controls are needed, but they should be defined in a way
that fits the raw-data-only scope and the planned `typer` migration.

## Definition of Done

- [ ] Define the supported runtime options for scraper execution, including region selection, page limits, and estate count limits.
- [ ] Define how storage backend selection should be exposed through the CLI.
- [ ] Document which options are required, optional, or mutually exclusive.
- [ ] Ensure the option design can be implemented cleanly in the Typer CLI planned in `TASK-007`.

## Notes

- Avoid options that expose legacy enrichment or API-delivery behavior.
- Prefer names and defaults that are explicit and safe for development runs.
