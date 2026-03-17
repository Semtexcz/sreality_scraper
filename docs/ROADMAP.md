# Roadmap

## Near Term

- Align the runtime flow with the raw-data-only project scope.
- Remove or isolate enrichment and normalization steps from the scraper path.
- Decide whether raw outputs should be stored in MongoDB or on the filesystem.
- Define the raw artifact format for downloaded listing records.

## Medium Term

- Add CLI options for limiting regions, pages, or estate counts.
- Add deterministic fixture-based tests for raw page capture and parsing.
- Define idempotent storage behavior for repeated downloads of the same listing.
- Replace ad hoc sleep-based throttling with explicit rate-limit handling.

## Longer Term

- Separate acquisition and persistence behind a minimal raw-data pipeline.
- Reassess whether auxiliary reference datasets are still required.
- Generate refreshed API docs from the stabilized module layout.
