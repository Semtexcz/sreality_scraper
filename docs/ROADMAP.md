# Roadmap

The roadmap is tracked by implementation stage instead of time horizon. Checked
items represent functionality or project outcomes already delivered in the current
repository. Unchecked items represent the next supported milestones.

## Scraper Stage

- [x] Collect raw apartment sale listings from `sreality.cz`.
- [x] Parse listing pages and detail pages into scraper-owned raw contracts.
- [x] Persist immutable raw snapshots to the filesystem.
- [x] Persist immutable raw snapshots to MongoDB.
- [x] Expose a public CLI for raw acquisition with region, page, estate, and
  storage-backend options.
- [x] Cover the scraper runtime with deterministic unit tests and an opt-in live
  integration test.
- [x] Harden runtime behavior around HTTP failures, response validation, and markup
  drift.
- [x] Revisit stop conditions and traversal assumptions that currently depend on
  simple listing-page HTML parsing.

## Normalization Stage

- [x] Define a typed `NormalizedListingRecord` contract owned by the normalization
  package.
- [x] Implement deterministic raw-to-normalized mapping from scraper outputs only.
- [x] Preserve unmapped raw source fields for traceability.
- [x] Keep normalization isolated from downstream enrichment and modeling modules.
- [x] Broaden normalized field coverage beyond the current title, price, building,
  and basic location mapping.
- [x] Replace title-text heuristics with clearer field-level extraction rules where
  the source payload allows it.
- [ ] Expose normalization as a supported operator-facing workflow instead of an
  internal component only.

## Enrichment Stage

- [x] Define a typed `EnrichedListingRecord` contract owned by the enrichment
  package.
- [x] Compute deterministic derived features from normalized records only.
- [x] Preserve the full normalized input record for downstream traceability.
- [x] Keep enrichment isolated from scraper-owned raw contracts.
- [ ] Expand the derived feature set beyond the initial pricing, disposition, area,
  and location flags.
- [ ] Reduce reliance on regex parsing of normalized title text for feature
  derivation.
- [ ] Expose enrichment as a supported operator-facing workflow instead of an
  internal component only.

## Modeling Stage

- [x] Define a typed `ModelingInputRecord` contract owned by the modeling package.
- [x] Build model-ready feature and target sets from enriched records only.
- [x] Attach explicit lineage and version metadata to modeling inputs.
- [x] Keep modeling isolated from direct raw and normalized record access.
- [ ] Introduce supported workflows that consume modeling inputs directly, such as
  dataset export, training preparation, or scoring-oriented orchestration.
- [ ] Decide whether modeling outputs should remain transient or gain persistence
  adapters.
- [ ] Reevaluate whether a public API or service surface is needed once modeling
  becomes part of the supported runtime contract.

## Pipeline and Operations

- [x] Establish explicit one-way module boundaries for `scraper`,
  `normalization`, `enrichment`, and `modeling`.
- [x] Implement an internal synchronous linear pipeline service from raw collection
  to modeling inputs.
- [x] Keep the public runtime intentionally centered on raw acquisition and
  persistence.
- [ ] Expose the internal linear pipeline behind a deliberate user-facing
  entrypoint without weakening the raw-only workflow.
- [ ] Decide which stage outputs, if any, should gain first-class persistence
  adapters beyond raw records.
- [ ] Expand integration coverage so full stage handoffs are verified against
  representative real-world payloads, not only fixture-driven unit tests.
- [ ] Refresh developer-facing documentation once the supported runtime surface for
  later stages is finalized.
- [ ] Reassess whether the bundled CSV reference datasets in `data/` still belong
  in the active codebase or should be archived as historical artifacts.
