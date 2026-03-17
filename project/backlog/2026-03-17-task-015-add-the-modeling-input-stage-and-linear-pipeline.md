---
task: TASK-015
status: "backlog"
priority: P2
type: feature
---

# Add the modeling input stage and linear pipeline wiring

Task: TASK-015
Status: backlog
Priority: P2
Type: feature
Author:
Created: 2026-03-17
Related: TASK-010, TASK-011, TASK-012, TASK-013, TASK-014

## Problem

The target architecture is not complete until the codebase exposes one simple
end-to-end path from raw scraping to model-ready inputs. Modeling should not depend on
raw or merely normalized data directly, and the final pipeline should remain a simple
in-process linear flow.

## Definition of Done

- [ ] Define the model-ready record or dataset contract consumed by the modeling boundary.
- [ ] Implement the contract as a typed Python model.
- [ ] Place the contract/component in the appropriate module boundary.
- [ ] Implement a modeling input component that accepts enriched records only.
- [ ] Introduce a simple in-process pipeline flow that composes scraper, normalization, enrichment, and modeling in sequence.
- [ ] Include a `model_version` field in the model-ready contract when a versioned model contract is introduced.
- [ ] Ensure each stage communicates only via explicit contracts, not shared mutable state.
- [ ] Ensure the pipeline remains optional and does not break the existing raw-only acquisition path.
- [ ] Add regression tests for the stage handoff contracts across the full linear pipeline.

## Notes

- Keep the execution model synchronous and local to the current Python application unless a later task proves otherwise.
- Do not introduce a message broker, workflow engine, or multi-repository split.
- Prefer explicit composition in application services over hidden framework magic.
