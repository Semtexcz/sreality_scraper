---
task: TASK-017
status: "todo"
priority: P1
type: feature
---

# Add response and markup validation for scraper pages

Task: TASK-017
Status: todo
Priority: P1
Type: feature
Author:
Created: 2026-03-17
Related: TASK-009, TASK-016

## Problem

The current parsers accept listing and detail HTML with almost no structural
validation. If `sreality.cz` changes important markup, the scraper can emit empty
or incomplete raw payloads while still appearing successful.

## Definition of Done

- [ ] Define explicit validation rules for minimum expected listing-page and
      detail-page structure before parser output is accepted.
- [ ] Detect and surface markup-drift conditions such as missing listing links,
      empty detail payloads, or absent key elements that previously anchored the
      raw contract.
- [ ] Ensure invalid pages fail clearly with scraper-stage validation errors rather
      than silently producing low-value records.
- [ ] Preserve the existing raw payload goal by validating page structure without
      normalizing or enriching extracted values.
- [ ] Add representative fixture-based tests for valid pages, malformed pages, and
      known markup-drift scenarios.
- [ ] Document any new parser assumptions in the scraper-stage technical docs or
      module docstrings.

## Notes

- Validation should be strict enough to catch scraper breakage but not so strict
  that harmless content variation causes false positives.
- Prefer parser-local invariants over ad hoc checks spread through orchestration
  code.
