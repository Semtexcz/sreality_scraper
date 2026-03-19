# Task Sequence

Recommended implementation order for the current backlog after completing
`TASK-050`.

| Order | Task | Focus | Phase | Why now |
| --- | --- | --- | --- | --- |
| 1 | `TASK-051` | Source-backed raw coordinate parsing | Scraper and normalization implementation | The raw contract is now approved, so the next critical step is to emit `source_payload.source_coordinates` and make normalization prefer it over legacy HTML replay. |
| 2 | `TASK-046` | Price surface and uncertainty workflow | Spatial analytics design | Still valuable, but it no longer blocks the coordinate-source fix for future raw captures and should follow the raw-coordinate implementation work. |

## Batches

| Batch | Tasks |
| --- | --- |
| Raw-coordinate implementation | `TASK-051` |
| Spatial analytics design | `TASK-046` |
