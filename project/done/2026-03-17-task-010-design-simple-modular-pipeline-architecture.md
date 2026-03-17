---
task: TASK-010
status: "done"
priority: P1
type: design
---

# Design the simple modular pipeline target architecture

Task: TASK-010
Status: done
Priority: P1
Type: design
Author:
Created: 2026-03-17
Related: TASK-011, TASK-012, TASK-013, TASK-014, TASK-015

## Problem

The current project documentation and module layout are centered on raw acquisition
and persistence only. To evolve the codebase toward a simple in-repo pipeline, the
project needs an explicit target architecture that introduces `scraper`,
`normalization`, `enrichment`, and `modeling` boundaries without adding extra
services, repositories, brokers, or orchestration platforms.

## Definition of Done

- [x] Document the target module boundaries for `scraper`, `normalization`, `enrichment`, and `modeling` inside the existing Python project.
- [x] Define the one-way dependency flow from scraper to normalization to enrichment to modeling.
- [x] Define the record contract expected at each stage boundary.
- [x] Require each stage boundary contract to be implemented as a typed Python model.
- [x] Require each contract and component to live in the appropriate module boundary.
- [x] Explicitly state that the scraper collects raw facts only, normalization produces stable structured data, enrichment computes derived features, and modeling consumes enriched data only.
- [x] Update the architecture and module documentation so later implementation tasks can execute against one approved design.

## Notes

- Keep the design inside one repository and one Python project.
- Do not introduce microservices, message brokers, background workers, or external orchestrators.
- Favor the smallest migration path that preserves the existing raw-acquisition runtime while opening room for later stages.
