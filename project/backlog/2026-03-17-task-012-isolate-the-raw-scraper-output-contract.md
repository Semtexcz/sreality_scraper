---
task: TASK-012
status: "backlog"
priority: P1
type: refactor
---

# Isolate the raw scraper output contract

Task: TASK-012
Status: backlog
Priority: P1
Type: refactor
Author:
Created: 2026-03-17
Related: TASK-010, TASK-011, TASK-013, TASK-015

## Problem

The current acquisition flow builds persistence-oriented record objects directly.
That couples scraping to downstream storage and makes it harder to introduce later
pipeline stages with clean handoff contracts. The scraper stage should emit raw facts
only and remain independent from normalization, enrichment, and modeling concerns.

## Definition of Done

- [ ] Define a raw scraper output model owned by the scraper boundary.
- [ ] Implement the contract as a typed Python model.
- [ ] Place the contract/component in the appropriate module boundary.
- [ ] Refactor the scraper runtime so it emits raw records before any downstream transformation or storage-specific adaptation.
- [ ] Keep source provenance needed for later stages, including listing identity and capture metadata.
- [ ] Include a `parser_version` field in the raw contract.
- [ ] Ensure the raw contract is JSON-serializable.
- [ ] Ensure the raw scraper contract excludes normalized fields, enriched features, and model-oriented attributes.
- [ ] Update or add tests proving the scraper output remains raw and source-faithful.

## Notes

- This task should preserve the current project goal that raw source data is captured without mutation.
- Storage adapters may still persist raw records, but they should depend on the scraper contract instead of defining it.
- Execute this task before implementing normalization logic.
