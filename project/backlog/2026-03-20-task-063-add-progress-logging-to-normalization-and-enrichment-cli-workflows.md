---
task: TASK-063
status: "backlog"
priority: P1
type: feature
---

# Add progress logging to normalization and enrichment CLI workflows

Task: TASK-063
Status: backlog
Priority: P1
Type: feature
Author:
Created: 2026-03-20
Related: TASK-021, TASK-034, TASK-062

## Problem

The `scraperweb normalize` and `scraperweb enrich` commands currently process
large filesystem datasets without any operator-visible runtime progress. On
larger batches, the CLI can look stalled even when work is still advancing
normally. Operators need explicit progress logging that makes long-running
normalization and enrichment runs observable without requiring ad hoc debug
instrumentation.

## Definition of Done

- [ ] Add operator-visible progress reporting for `scraperweb normalize` and
      `scraperweb enrich` so long-running runs emit clear runtime activity.
- [ ] Report the selected workflow scope at startup and show cumulative
      processed-record progress during the run.
- [ ] Keep default terminal output concise for large datasets while still
      making forward progress visible; avoid per-record noise unless an
      explicitly more verbose mode is enabled.
- [ ] Reuse or extend the existing CLI/reporting architecture where practical
      instead of adding one-off workflow-specific print statements.
- [ ] Add or update deterministic tests that cover the new normalization and
      enrichment progress-reporting behavior.
- [ ] Update operator-facing CLI documentation if new logging or verbosity
      options are introduced.

## Notes

- Favor a shared progress-reporting abstraction for non-scrape batch workflows
  so later CLI stages can follow the same operator experience.
- The logger should help distinguish a legitimately active long run from a hung
  process, especially for region-wide reprocessing jobs.
- Preserve the existing workflow semantics and artifact contents; this task is
  about observability, not changing normalization or enrichment results.
