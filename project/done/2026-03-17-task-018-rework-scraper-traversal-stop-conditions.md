---
task: TASK-018
status: "done"
priority: P1
type: feature
---

# Rework scraper traversal stop conditions

Task: TASK-018
Status: done
Priority: P1
Type: feature
Author:
Created: 2026-03-17
Related: TASK-005, TASK-009, TASK-016, TASK-017

## Problem

The current scraper decides how far to traverse listing pages by parsing simple
pagination anchors and assuming the inferred page count is trustworthy. That
approach is fragile when pagination markup changes, when pages contain fewer
results than expected, or when duplicate and empty pages appear near the end of a
region traversal.

## Definition of Done

- [x] Revisit the current page traversal algorithm and document the supported stop
      conditions for region scraping.
- [x] Replace the current `max(strana) + 1` pagination assumption with traversal
      logic that can stop based on observed listing-page outcomes rather than a
      single HTML heuristic.
- [x] Define explicit handling for empty listing pages, repeated estate URL sets,
      and other signals that indicate traversal exhaustion or upstream drift.
- [x] Ensure region traversal remains bounded by operator-supplied `max_pages` and
      `max_estates` limits.
- [x] Add deterministic unit tests for multi-page traversal, early-stop behavior,
      duplicate-page detection, and pagination drift cases.
- [x] Update operator-facing documentation if runtime semantics for page traversal
      change.

## Notes

- Keep traversal synchronous and simple unless a later task justifies a more
  complex crawler strategy.
- Prefer explicit page-iteration state over implicit assumptions hidden in parser
  helpers.
