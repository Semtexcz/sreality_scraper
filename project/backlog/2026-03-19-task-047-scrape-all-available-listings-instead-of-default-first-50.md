---
task: TASK-047
status: "todo"
priority: P1
type: feature
---

# Scrape all available listings instead of the default first 50

Task: TASK-047
Status: todo
Priority: P1
Type: feature
Author:
Created: 2026-03-19
Related: TASK-001

## Problem

The current `scraperweb scrape` behavior stops after the first `50` listings
unless an operator explicitly overrides the estate limit. That default causes
partial datasets, makes routine runs easy to misinterpret as complete crawls,
and conflicts with the expected scraper behavior of collecting all currently
available listings for the selected region unless the operator opts into a
smaller bounded run.

## Definition of Done

- [ ] Change the default scrape behavior so `scraperweb scrape` continues across
      listing pages until all currently available listing detail URLs have been
      processed, unless an explicit runtime limit stops the run.
- [ ] Preserve operator-controlled caps such as `--max-pages` and
      `--max-estates` so bounded test and sampling runs still work when
      requested.
- [ ] Update progress or operator-facing output if needed so unbounded-by-default
      estate collection is explicit during runtime.
- [ ] Add or update regression coverage for CLI option defaults and acquisition
      orchestration so the scraper no longer silently stops at `50` estates.
- [ ] Document any changed default behavior in the relevant operator-facing
      documentation and changelog entry when the task is implemented.

## Notes

- Prefer an explicit unlimited default over a hidden numeric ceiling.
- The stop condition should remain deterministic: finish when pagination is
  exhausted or an explicit operator limit is reached.
- Avoid changing the meaning of explicit limit flags while removing the
  surprising default cap.
