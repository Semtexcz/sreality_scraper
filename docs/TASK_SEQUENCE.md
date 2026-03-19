# Task Sequence

Recommended implementation order for the current backlog after completing
`TASK-045`.

| Order | Task | Focus | Phase | Why now |
| --- | --- | --- | --- | --- |
| 1 | `TASK-048` | Source-backed detail-coordinate contract | Coordinate-source design | Defines how embedded Sreality locality coordinates should be modeled and prioritized before implementation changes the normalization and enrichment contracts. |
| 2 | `TASK-049` | Source-backed detail coordinate parsing | Coordinate-source implementation | Captures real listing GPS from detail HTML and prevents the current fallback geocoding from overwriting better source-backed coordinates. |
| 3 | `TASK-046` | Price surface and uncertainty workflow | Spatial analytics design | Depends on the strongest available coordinate source order so any map-ready surface design is based on the implemented location precision stack. |

## Batches

| Batch | Tasks |
| --- | --- |
| Coordinate-source design | `TASK-048` |
| Coordinate-source implementation | `TASK-049` |
| Spatial analytics design | `TASK-046` |
