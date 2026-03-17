# Roadmap

## Near Term

- Design the target raw-data architecture and refactor boundaries.
- Refactor the scraper into explicit services and classes with clear responsibilities.
- Decide whether raw outputs should be stored in MongoDB or on the filesystem.
- Build a `typer` CLI that exposes the refactored runtime safely.

## Medium Term

- Add CLI options for limiting regions, pages, or estate counts.
- Add deterministic fixture-based tests for raw page capture and parsing.
- Define idempotent storage behavior for repeated downloads of the same listing.
- Remove legacy enrichment and output flows that do not match the project goal.
- Replace ad hoc sleep-based throttling with explicit rate-limit handling.

## Longer Term

- Separate acquisition and persistence behind a minimal raw-data pipeline.
- Reassess whether auxiliary reference datasets are still required.
- Generate refreshed API docs from the stabilized module layout.
