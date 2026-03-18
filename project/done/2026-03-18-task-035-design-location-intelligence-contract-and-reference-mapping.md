---
task: TASK-035
status: "done"
priority: P1
type: design
---

# Design location intelligence contract and reference mapping

Task: TASK-035
Status: done
Priority: P1
Type: design
Author:
Created: 2026-03-18
Related: TASK-019, TASK-029, TASK-032

## Problem

Location is expected to be the strongest driver of apartment asking prices, but
the current pipeline stops at `city`, `city_district`, and `nearby_places`
without a deliberate contract for administrative mapping, reference-data joins,
coordinate provenance, or spatial feature semantics. Without that design, later
implementation work will drift into ad hoc heuristics and unstable model inputs.

## Definition of Done

- [x] Define where reference-backed location intelligence belongs across
      normalization, enrichment, and modeling boundaries.
- [x] Decide the canonical fields for municipality identity, administrative codes,
      coordinates, district-center membership, and spatial buckets.
- [x] Document the provenance and fallback rules for joining normalized locations
      to bundled reference datasets such as `data/souradnice.csv`,
      `data/OkresniMesta.csv`, and `data/ObceSRozsirenouPusobnosti.csv`.
- [x] Define how ambiguous municipality names, Prague-style numbered districts,
      and missing district labels should be represented without hiding uncertainty.
- [x] Identify any contract version bumps required by the proposed location
      intelligence fields.

## Notes

- Keep direct source reshaping in normalization and derived interpretation in
  enrichment; do not collapse both concerns into one stage.
- The design should make room for both human-readable names and stable coded
  identifiers.
- Prefer explicit provenance fields over silent best-effort matching.

## Design Decision

Reference-backed location intelligence belongs in the enrichment stage, not in
normalization. `NormalizedLocation` should remain limited to facts directly
reshaped from the source payload or deterministic title fallback parsing. This
keeps normalization source-backed and idempotent without introducing external
lookup semantics, match confidence, or derived spatial interpretation.

The first implementation task should extend `EnrichedListingRecord` with a new
top-level `location_features` sub-contract that is parallel to the existing
`price_features` and `property_features` groups. Modeling should not receive the
full enrichment sub-contract automatically; `TASK-039` should flatten only the
approved stable subset into `ModelingFeatureSet`.

## Proposed Contract Ownership

### Normalization

Normalization keeps ownership of:

- `location.location_text`
- `location.city`
- `location.city_district`
- `location.location_descriptor`
- per-field source provenance such as `city_source`
- raw nearby-place facts already mapped into `location.nearby_places`

Normalization should not add municipality codes, region codes, coordinates,
district-center flags, or spatial bucket identifiers because those values are
not direct source facts from `sreality.cz`.

### Enrichment

Enrichment should own one future `EnrichedLocationFeatures` contract with four
logical groups:

- reference-backed administrative identity
- coordinate resolution and provenance
- district-center and metropolitan context
- spatial bucketing and match traceability

The canonical fields should be:

- `municipality_name: str | None`
- `municipality_code: str | None`
- `district_name: str | None`
- `district_code: str | None`
- `region_name: str | None`
- `region_code: str | None`
- `orp_name: str | None`
- `orp_code: str | None`
- `latitude: float | None`
- `longitude: float | None`
- `coordinate_source: str | None`
- `is_district_center_municipality: bool | None`
- `district_center_name: str | None`
- `district_center_code: str | None`
- `metropolitan_district_name: str | None`
- `metropolitan_district_code: str | None`
- `spatial_cell_1km_id: str | None`
- `spatial_cell_250m_id: str | None`
- `municipality_match_status: str`
- `municipality_match_method: str | None`
- `municipality_match_input: str | None`
- `municipality_match_candidates: tuple[str, ...]`
- `derivation_notes: tuple[str, ...]`

All fields stay optional except `municipality_match_status`, which should always
be one of `matched`, `ambiguous`, or `unmatched`. Human-readable names and
stable codes should be stored together so downstream consumers do not need to
rejoin reference tables just to interpret one code.

### Modeling

Modeling should receive only the location features that remain stable after the
enrichment contract proves out. The approved handoff should be deferred to
`TASK-039`, but the intended candidate set is:

- municipality and region identifiers
- Prague or metropolitan district identifiers when deterministically matched
- coordinate fields or distance-derived metrics already approved by enrichment
- stable spatial cell identifiers
- boolean flags such as district-center membership

Match-candidate arrays and free-form derivation notes should remain enrichment
traceability metadata and should not be flattened into `ModelingFeatureSet`.

## Reference Mapping Sources And Provenance Rules

The bundled datasets should be joined in enrichment with explicit provenance:

- `data/souradnice.csv` is the canonical municipality-coordinate source and also
  supplies municipality, district, and region names and codes.
- `data/OkresniMesta.csv` is the canonical district-center source keyed by
  district identity.
- `data/ObceSRozsirenouPusobnosti.csv` is the canonical ORP source keyed by ORP
  code and name.

The match order should be deterministic and recorded in
`municipality_match_method`:

1. Match by normalized `location.city` when it maps cleanly to one municipality.
2. For Prague-style numbered inputs such as `Praha 8`, normalize municipality
   identity to `Praha` and treat the numbered suffix as district-level context,
   not as a municipality name.
3. Use `location.location_text` only as a secondary disambiguation input when
   `city` alone is insufficient.
4. Use `location.city_district` only for district- or metropolitan-level
   interpretation, never as the sole municipality key.

`municipality_match_input` should record the normalized value that drove the
selected match. `coordinate_source` should distinguish whether coordinates came
from a municipality reference row, a future district-level override, or remain
missing.

## Uncertainty Representation

Ambiguity must stay explicit:

- If multiple municipalities share the same candidate name and no approved
  disambiguation rule resolves them, set `municipality_match_status` to
  `ambiguous`, leave the resolved municipality and coordinate fields empty, and
  populate `municipality_match_candidates`.
- If no reference row matches the normalized input, set
  `municipality_match_status` to `unmatched` and keep all derived fields empty.
- If a Prague listing contains `Praha` without a district label, municipality
  identity may still be `matched` to `Praha`, while district-specific fields
  remain `None`.
- If `city_district` is absent for non-Prague municipalities, that absence must
  remain explicit and must not trigger guessed district-center or metropolitan
  assignments.

This design intentionally favors visible uncertainty over partially guessed
codes or coordinates.

## Contract Version Impact

`TASK-035` itself does not require a stage-contract version bump because it
documents the design only. The planned implementation impact is:

- `TASK-036` should bump enrichment from `enriched-listing-v2` to
  `enriched-listing-v3` when the first `location_features` fields land.
- `TASK-037` and `TASK-038` may keep the same enrichment version only if they
  stay strictly additive within the approved `location_features` contract;
  otherwise they should bump it again.
- `TASK-039` should bump modeling inputs from `modeling-input-v2` to
  `modeling-input-v3` when approved location features are propagated into
  `ModelingFeatureSet`.
- No normalization contract bump is required for this design because reference
  mapping is intentionally deferred out of `NormalizedLocation`.
