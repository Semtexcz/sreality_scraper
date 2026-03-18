# Task Sequence

Recommended implementation order for the current backlog after completing
`TASK-036`.

| Order | Task | Focus | Phase | Why now |
| --- | --- | --- | --- | --- |
| 1 | `TASK-037` | Coordinates and macro distances | Foundation | Builds the first strong spatial feature layer on top of the new administrative mapping. |
| 2 | `TASK-029` | Area-based pricing features | Core enrichment | Removes title regex dependence for area-derived pricing. |
| 3 | `TASK-030` | Building semantics | Core enrichment | Adds typed building interpretation from normalized fields. |
| 4 | `TASK-031` | Accessories and outdoor space | Core enrichment | Reuses typed accessories already present in normalization outputs. |
| 5 | `TASK-032` | Nearby-place accessibility | Core enrichment | Adds micro-location and amenity accessibility signals. |
| 6 | `TASK-033` | Listing freshness and lifecycle | Core enrichment | Adds deterministic temporal features from normalized dates. |
| 7 | `TASK-038` | Metropolitan districts and spatial cells | Urban refinement | Refines location features for Prague and other large cities. |
| 8 | `TASK-039` | Modeling input propagation | Modeling handoff | Pushes approved location features into `ModelingFeatureSet`. |
| 9 | `TASK-034` | Operator-facing enrichment workflow | Workflow | Expose replay only after the enrichment contract is more stable. |

## Batches

| Batch | Tasks |
| --- | --- |
| Foundation | `TASK-037` |
| Core enrichment | `TASK-029`, `TASK-030`, `TASK-031`, `TASK-032`, `TASK-033` |
| Urban and modeling | `TASK-038`, `TASK-039` |
| Workflow | `TASK-034` |
