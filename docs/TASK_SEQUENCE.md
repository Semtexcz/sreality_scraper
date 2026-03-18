# Task Sequence

Recommended implementation order for the current backlog after completing
`TASK-037`.

| Order | Task | Focus | Phase | Why now |
| --- | --- | --- | --- | --- |
| 1 | `TASK-029` | Area-based pricing features | Core enrichment | Removes title regex dependence for area-derived pricing. |
| 2 | `TASK-030` | Building semantics | Core enrichment | Adds typed building interpretation from normalized fields. |
| 3 | `TASK-031` | Accessories and outdoor space | Core enrichment | Reuses typed accessories already present in normalization outputs. |
| 4 | `TASK-032` | Nearby-place accessibility | Core enrichment | Adds micro-location and amenity accessibility signals. |
| 5 | `TASK-033` | Listing freshness and lifecycle | Core enrichment | Adds deterministic temporal features from normalized dates. |
| 6 | `TASK-038` | Metropolitan districts and spatial cells | Urban refinement | Refines location features for Prague and other large cities. |
| 7 | `TASK-039` | Modeling input propagation | Modeling handoff | Pushes approved location features into `ModelingFeatureSet`. |
| 8 | `TASK-034` | Operator-facing enrichment workflow | Workflow | Expose replay only after the enrichment contract is more stable. |

## Batches

| Batch | Tasks |
| --- | --- |
| Core enrichment | `TASK-029`, `TASK-030`, `TASK-031`, `TASK-032`, `TASK-033` |
| Urban and modeling | `TASK-038`, `TASK-039` |
| Workflow | `TASK-034` |
