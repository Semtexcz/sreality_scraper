---
task: TASK-062
status: "done"
priority: P1
type: feature
---

# Add resumable scrape mode that skips existing listings

Task: TASK-062
Status: done
Priority: P1
Type: feature
Author:
Created: 2026-03-19
Related: TASK-006, TASK-007, TASK-061

## Problem

When a long scraper run fails partway through, the operator currently has to
restart from the beginning and the scraper will re-download detail pages for
listings that are already persisted. That wastes time, increases load on the
source site, and makes recovery from transient failures unnecessarily slow.
The CLI needs an explicit resume-oriented mode that can detect already stored
listing records and skip them while continuing to collect only missing
listings.

## Definition of Done

- [ ] Add a CLI option that enables a resumable scrape mode for supported
      storage backends.
- [ ] Define how the scraper determines that a listing already exists for the
      current region and backend, including any listing-id or source-URL
      identity rules.
- [ ] Update the acquisition flow so already persisted listings are skipped
      before detail-page download and persistence work begins.
- [ ] Preserve existing default behavior for operators who want a fresh scrape
      without resume semantics.
- [ ] Add progress reporting that makes skipped-existing listings visible during
      runtime without overwhelming normal terminal output.
- [ ] Add or update deterministic tests for filesystem and any supported
      backend-specific existence checks, skip behavior, and CLI wiring.
- [ ] Update operator-facing documentation for the new resume workflow and its
      limitations.

## Notes

- Favor an explicit opt-in flag over implicit auto-resume behavior.
- The design should make partial reruns cheaper without hiding when existing
  data prevented a detail page from being fetched again.
- Resume behavior should be compatible with the traversal-hardening work so a
  recovered crawl can continue across the remaining listing pages safely.
