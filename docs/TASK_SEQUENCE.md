# Task Sequence

Recommended implementation order for the current backlog after completing
`TASK-030`.

| Order | Task | Focus | Phase | Why now |
| --- | --- | --- | --- | --- |
| 1 | `TASK-031` | Accessories and outdoor space | Core enrichment | Reuses typed accessories already present in normalization outputs. |
| 2 | `TASK-032` | Nearby-place accessibility | Core enrichment | Adds micro-location and amenity accessibility signals. |
| 3 | `TASK-033` | Listing freshness and lifecycle | Core enrichment | Adds deterministic temporal features from normalized dates. |
| 4 | `TASK-038` | Metropolitan districts and spatial cells | Urban refinement | Refines location features for Prague and other large cities. |
| 5 | `TASK-039` | Modeling input propagation | Modeling handoff | Pushes approved location features into `ModelingFeatureSet`. |
| 6 | `TASK-034` | Operator-facing enrichment workflow | Workflow | Expose replay only after the enrichment contract is more stable. |

## Batches

| Batch | Tasks |
| --- | --- |
| Core enrichment | `TASK-031`, `TASK-032`, `TASK-033` |
| Urban and modeling | `TASK-038`, `TASK-039` |
| Workflow | `TASK-034` |
