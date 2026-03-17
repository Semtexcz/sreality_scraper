# Roadmap

## Near Term

- Add automated tests for parsing and transformation helpers.
- Extract HTTP and MongoDB operations behind smaller testable units.
- Add structured logging around failures and retryable operations.
- Define a stable output schema for posted estate payloads.

## Medium Term

- Add CLI options for limiting regions, pages, or estate counts.
- Add deduplication or idempotency strategy for repeated scraper runs.
- Introduce a local fixture set for deterministic scraper parsing tests.
- Replace ad hoc sleep-based throttling with explicit rate-limit handling.

## Longer Term

- Separate scraping, enrichment, and persistence into clearer pipeline stages.
- Add validation for incoming CSV reference datasets.
- Generate refreshed API docs from the refactored module layout.
