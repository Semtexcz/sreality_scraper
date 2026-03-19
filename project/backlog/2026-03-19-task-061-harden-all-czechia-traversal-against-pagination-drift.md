---
task: TASK-061
status: "backlog"
priority: P1
type: fix
---

# Harden all-Czechia traversal against pagination drift

Task: TASK-061
Status: backlog
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

- [ ] Reproduce and document the current premature-stop behavior for long
      `all-czechia` traversals, including the observed stop reason and the page
      context that triggered it.
- [ ] Design and implement a traversal strategy that is more robust to
      pagination drift than the current single-page duplicate stop condition.
- [ ] Persist or log enough terminating listing-page diagnostics to explain why
      a run stopped without requiring a live re-run against the site.
- [ ] Preserve deterministic protection against true duplicate tail pages so the
      scraper does not loop indefinitely when the website starts repeating the
      same listing windows.
- [ ] Add or update deterministic tests covering duplicate pages, temporary
      duplicate windows, and eventual traversal exhaustion.
- [ ] Update operator-facing documentation if stop semantics or diagnostics
      change.

## Notes

- Favor explicit stop-reason reporting over silent early returns.
- Do not trust the visible result counter on the site as the sole completeness
  signal; base traversal on observed listing behavior.
- The solution should distinguish between a repeated tail, a transient duplicate
  window, and a genuinely exhausted listing set.
