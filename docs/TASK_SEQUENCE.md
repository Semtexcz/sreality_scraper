# Task Sequence

Recommended implementation order for the current backlog after completing
`TASK-032`.

| Order | Task | Focus | Phase | Why now |
| --- | --- | --- | --- | --- |
| 1 | `TASK-033` | Listing freshness and lifecycle | Core enrichment | Adds deterministic temporal features from normalized dates. |
| 2 | `TASK-038` | Metropolitan districts and spatial cells | Urban refinement | Refines location features for Prague and other large cities. |
| 3 | `TASK-039` | Modeling input propagation | Modeling handoff | Pushes approved location features into `ModelingFeatureSet`. |
| 4 | `TASK-034` | Operator-facing enrichment workflow | Workflow | Expose replay only after the enrichment contract is more stable. |

## Batches

| Batch | Tasks |
| --- | --- |
| Core enrichment | `TASK-033` |
| Urban and modeling | `TASK-038`, `TASK-039` |
| Workflow | `TASK-034` |
