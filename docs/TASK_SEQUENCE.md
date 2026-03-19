# Task Sequence

Recommended implementation order for the current backlog after completing
`TASK-048`.

| Order | Task | Focus | Phase | Why now |
| --- | --- | --- | --- | --- |
| 1 | `TASK-049` | Source-backed detail coordinate parsing | Coordinate-source implementation | Implements the approved contract so normalized source-backed listing coordinates become available and enrichment can prefer them over fallback geocoding. |
| 2 | `TASK-046` | Price surface and uncertainty workflow | Spatial analytics design | Depends on the implemented coordinate-source priority so map-ready surface design is based on the actual winning location stack rather than the old fallback-only behavior. |

## Batches

| Batch | Tasks |
| --- | --- |
| Coordinate-source implementation | `TASK-049` |
| Spatial analytics design | `TASK-046` |
