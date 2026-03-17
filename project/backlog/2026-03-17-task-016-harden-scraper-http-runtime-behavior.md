---
task: TASK-016
status: "todo"
priority: P1
type: feature
---

# Harden scraper HTTP runtime behavior

Task: TASK-016
Status: todo
Priority: P1
Type: feature
Author:
Created: 2026-03-17
Related: TASK-005, TASK-007, TASK-009

## Problem

The scraper runtime currently treats every HTTP response as successful HTML and
does not distinguish transient transport failures from invalid responses. This
makes raw acquisition brittle, obscures operator-visible failure modes, and
creates avoidable partial-run instability.

## Definition of Done

- [ ] Introduce explicit scraper-stage HTTP error handling for request failures,
      non-success status codes, and missing response content.
- [ ] Define scraper-owned exception types or result contracts so runtime callers
      can distinguish retryable transport failures from unrecoverable response
      errors.
- [ ] Add bounded retry behavior with explicit timeout handling for transient
      network failures without creating unbounded loops.
- [ ] Ensure the acquisition flow records or logs enough context to identify the
      failed region, page, and listing URL.
- [ ] Keep the raw-only runtime contract intact and avoid introducing downstream
      normalization or enrichment behavior.
- [ ] Add deterministic unit tests that cover success, retry, and terminal-failure
      paths for listing-page and detail-page fetches.

## Notes

- Prefer explicit failure propagation over silent record skipping.
- Keep retry policy simple, configurable where needed, and limited to transport
  conditions that are genuinely transient.
- Avoid coupling the scraper runtime to storage-backend implementation details.
