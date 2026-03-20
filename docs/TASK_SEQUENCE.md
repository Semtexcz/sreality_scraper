# Task Sequence

Recommended implementation order for the current backlog after completing
`TASK-062`, with the CLI workflow observability fix now added ahead of the
notebook-analysis batch and production-model design work.

| Order | Task | Focus | Phase | Why now |
| --- | --- | --- | --- | --- |
| 1 | `TASK-063` | Progress logging for `normalize` and `enrich` | CLI observability | Large normalization and enrichment runs currently appear hung, so the operator-facing visibility gap should be closed before more long-running workflows accumulate on top of the current CLI. |
| 2 | `TASK-046` | Price surface and uncertainty workflow | Spatial analytics design | The approved notebook plan depends on a repository-level decision for scalar-field generation and uncertainty handling, so this older design task remains the prerequisite for map-oriented analytical work. |
| 3 | `TASK-053` | Notebook analysis-dataset contract | Modeling dataset design | The notebook and any later training stage need a canonical tabular projection before export, filtering, and article visuals can be implemented without semantic drift. |
| 4 | `TASK-054` | Analysis-dataset export workflow | Modeling workflow implementation | Once the dataset contract is approved, the repository needs a deterministic export path so notebooks and later training consume the same versioned inputs. |
| 5 | `TASK-055` | Reproducible notebook scaffold and environment | Analysis tooling | The scaffold should come after the dataset export path is clear so the first notebook starts on supported inputs rather than placeholder loading logic. |
| 6 | `TASK-056` | Grid-based price surface and uncertainty analysis | Spatial notebook implementation | This task turns the approved spatial-design decisions into the first article-ready scalar-field workflow backed by the exported analysis dataset. |
| 7 | `TASK-057` | Feature-influence reporting | Explanatory modeling | Once the notebook can consume the dataset, it can add grouped price-driver reporting without conflating raw correlation with model contribution. |
| 8 | `TASK-058` | Correlation and multicollinearity reporting | Explanatory modeling | Correlation and multicollinearity diagnostics should be added before the final interval notebook model so feature-reduction decisions remain explicit. |
| 9 | `TASK-059` | Predictive interval notebook model | Predictive modeling | The notebook should only add its first interval prediction workflow after the dataset, spatial outputs, and diagnostic sections are already defined. |
| 10 | `TASK-060` | Production training and scoring artifacts | Runtime design | The final design task should translate validated notebook outcomes into repository-level training and scoring contracts. |

## Batches

| Batch | Tasks |
| --- | --- |
| CLI observability | `TASK-063` |
| Spatial analytics design | `TASK-046` |
| Notebook dataset foundation | `TASK-053`, `TASK-054`, `TASK-055` |
| Notebook analytical outputs | `TASK-056`, `TASK-057`, `TASK-058`, `TASK-059` |
| Production modeling design | `TASK-060` |
