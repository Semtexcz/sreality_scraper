---
task: TASK-007
status: "done"
priority: P1
type: feature
---

# Build a Typer-based CLI for scraper operations

Task: TASK-007
Status: done
Priority: P1
Type: feature
Author:
Created: 2026-03-17
Related: TASK-003, TASK-004, TASK-006, TASK-009

## Problem

The project currently lacks a modern, explicit, and testable command-line interface.
The new runtime should be exposed through `typer`, with commands and options that map
cleanly to application services rather than embedding scraper logic in script wrappers.

## Definition of Done

- [x] Add `typer` as the CLI framework dependency.
- [x] Create a top-level CLI application with commands for scraping and auxiliary data-loading flows that are still required.
- [x] Implement runtime options for region selection, page limits, estate count limits, and storage backend selection.
- [x] Ensure CLI help text and validation reflect the raw-data-only scope.
- [x] Replace or retire legacy entrypoints that no longer match the target interface.
- [x] Keep command handlers thin and delegate work to application services.

## Notes

- CLI commands should construct runtime dependencies and call orchestrating services.
- Avoid duplicating option parsing logic across commands.
- The CLI surface should be stable enough to support future automation.
