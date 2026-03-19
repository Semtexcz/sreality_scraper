# Task Sequence

Recommended implementation order for the current backlog after completing
`TASK-049`.

| Order | Task | Focus | Phase | Why now |
| --- | --- | --- | --- | --- |
| 1 | `TASK-050` | Source-backed raw coordinate contract | Raw-contract design | The current GPS recovery still depends on `raw_page_snapshot`, so the scraper-owned raw boundary needs an approved contract before parser changes can remove that dependency for future captures. |
| 2 | `TASK-051` | Source-backed raw coordinate parsing | Scraper and normalization implementation | Depends on the approved raw contract so future raw artifacts can keep listing GPS without storing full detail HTML snapshots. |
| 3 | `TASK-046` | Price surface and uncertainty workflow | Spatial analytics design | Still valuable, but it no longer blocks the coordinate-source fix for future raw captures and should follow the scraper-contract work. |

## Batches

| Batch | Tasks |
| --- | --- |
| Raw-coordinate design | `TASK-050` |
| Raw-coordinate implementation | `TASK-051` |
| Spatial analytics design | `TASK-046` |
