---
task: TASK-061
status: "done"
priority: P1
type: fix
---

# Harden all-Czechia traversal against pagination drift

Task: TASK-061
Status: done
Priority: P1
Type: fix
Author:
Created: 2026-03-19
Related: TASK-047

## Problem

The current unbounded `all-czechia` traversal stops as soon as one listing page
contains no previously unseen detail URLs. In practice, long Sreality crawls
can drift while the result ordering changes underneath the scraper. A later
page may therefore contain only already-seen listings even though many further
pages still exist. This causes materially incomplete runs, such as a nationwide
apartment crawl stopping after 6,653 processed listings around page 307 while
the site still reported roughly 15 thousand results.

## Definition of Done

- [x] Reproduce and document the current premature-stop behavior for long
      `all-czechia` traversals, including the observed stop reason and the page
      context that triggered it.
- [x] Design and implement a traversal strategy that is more robust to
      pagination drift than the current single-page duplicate stop condition.
- [x] Persist or log enough terminating listing-page diagnostics to explain why
      a run stopped without requiring a live re-run against the site.
- [x] Preserve deterministic protection against true duplicate tail pages so the
      scraper does not loop indefinitely when the website starts repeating the
      same listing windows.
- [x] Add or update deterministic tests covering duplicate pages, temporary
      duplicate windows, and eventual traversal exhaustion.
- [x] Update operator-facing documentation if stop semantics or diagnostics
      change.

## Implementation Notes

- Reproduced the failure mode from the reported nationwide crawl: the previous
  collector semantics stopped immediately when page `307` yielded zero new
  detail URLs, even though this can be a transient duplicate window during
  `all-czechia` pagination drift rather than true traversal exhaustion.
- Hardened unbounded `all-czechia` traversal so one stale page without new
  listings no longer terminates the run. The collector now tolerates short
  stale windows, stops immediately on a repeated duplicate-tail signature, and
  otherwise stops after three consecutive stale pages without recovery.
- Added explicit traversal-stop diagnostics that report the stop reason, page
  number, observed estate count, newly discovered estate count, stale-page
  streak, and repeated-page origin when applicable.
- Added deterministic unit coverage for:
  temporary duplicate windows that later recover,
  repeated duplicate-tail pages,
  and stale-window exhaustion without recovery.

## Notes

- Favor explicit stop-reason reporting over silent early returns.
- Do not trust the visible result counter on the site as the sole completeness
  signal; base traversal on observed listing behavior.
- The solution distinguishes between a repeated tail, a transient duplicate
  window, and a genuinely exhausted listing set.
