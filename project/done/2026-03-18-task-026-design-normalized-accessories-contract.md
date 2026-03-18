---
task: TASK-026
status: "done"
priority: P1
type: design
---

# Design normalized accessories contract

Task: TASK-026
Status: done
Priority: P1
Type: design
Author:
Created: 2026-03-18
Related: TASK-019

## Problem

The raw `Příslušenství:` value is currently preserved as a hybrid string under
`core_attributes.source_specific_attributes`, even though the dataset already
contains repeated, parseable accessory semantics such as elevator presence,
barrier-free access, furnishing state, balcony or terrace area, and parking
capacity. A dedicated normalized contract is needed before implementation so the
new fields stay explicit and maintainable instead of becoming another
source-shaped overflow blob.

## Definition of Done

- [x] Define a typed normalized accessories contract with explicit ownership and
      field names.
- [x] Decide which recurring tokens should map to booleans, which should map to
      enums, and which should map to numeric area or count fields.
- [x] Define how repeated area-bearing features such as balcony, loggia,
      terrace, and cellar should be represented.
- [x] Define fallback handling for rare or ambiguous tokens such as
      `2 garáže` or any future unexpected accessory strings.
- [x] Document whether the original `Příslušenství:` text remains preserved as
      `source_text`, overflow, or both.

## Notes

- Current data analysis found 457 records with `Příslušenství:`.
- Frequent boolean or enum-like tokens include `Výtah`, `Bez výtahu`,
  `Bezbariérový přístup`, `Nemá bezbariérový přístup`, `Zařízeno`,
  `Částečně zařízeno`, and `Nezařízeno`.
- Frequent quantifiable tokens include `Balkon o ploše Xm²`,
  `Lodžie o ploše Xm²`, `Terasa o ploše Xm²`, `Sklep o ploše Xm²`, and
  `Parkovací stání s N místy`.

## Design Decision

Accessories should live under `core_attributes` because they describe direct
property amenities rather than geographic context, lifecycle state, or derived
analytics. The normalization contract should therefore add a new
`accessories: NormalizedAccessories` field to `NormalizedCoreAttributes`.

The typed contract should contain the following fields:

- `source_text: str | None`
- `has_elevator: bool | None`
- `is_barrier_free: bool | None`
- `furnishing_state: str | None`
- `balcony: NormalizedAccessoryAreaFeature`
- `loggia: NormalizedAccessoryAreaFeature`
- `terrace: NormalizedAccessoryAreaFeature`
- `cellar: NormalizedAccessoryAreaFeature`
- `parking_space_count: int | None`
- `unparsed_fragments: tuple[str, ...]`

`source_text` preserves the original `Příslušenství:` value exactly as received
from the source payload. `unparsed_fragments` stores supported-source accessory
tokens that cannot yet be represented safely in typed fields. The follow-up
implementation should use the comma-delimited normalized tail for tokenization
when the source value contains the duplicated leading concatenated fragment seen
in current raw snapshots.

The repeated area-bearing features should use one shared sub-contract so the
shape stays explicit and consistent across balcony, loggia, terrace, and
cellar:

- `is_present: bool | None`
- `area_sqm: float | None`

This keeps the contract fixed-width while still handling both `Balkon` and
`Balkon o ploše 6 m²` without introducing dynamic dictionaries or many
parallel boolean-plus-area top-level fields.

## Mapping Rules

The following recurring tokens should map to typed fields:

- `Výtah` -> `has_elevator = True`
- `Bez výtahu` -> `has_elevator = False`
- `Bezbariérový přístup` -> `is_barrier_free = True`
- `Nemá bezbariérový přístup` -> `is_barrier_free = False`
- `Zařízeno` -> `furnishing_state = "furnished"`
- `Částečně zařízeno` -> `furnishing_state = "partially_furnished"`
- `Nezařízeno` -> `furnishing_state = "unfurnished"`
- `Balkon` or `Balkon o ploše Xm²` -> `balcony`
- `Lodžie` or `Lodžie o ploše Xm²` -> `loggia`
- `Terasa` or `Terasa o ploše Xm²` -> `terrace`
- `Sklep` or `Sklep o ploše Xm²` -> `cellar`
- `Parkovací stání s N místy` -> `parking_space_count = N`

For area-bearing features, a bare presence token sets `is_present = True` and
leaves `area_sqm = None`. An area-bearing token sets `is_present = True` and
parses `area_sqm` from the source text. Missing tokens leave the feature at its
default empty state with both fields unset.

## Overflow And Compatibility Rules

Recognized accessory facts should stop being duplicated in
`core_attributes.source_specific_attributes` once they are mapped into
`core_attributes.accessories`. The typed `accessories` contract becomes the
canonical access path for supported accessory semantics.

The original raw `Příslušenství:` value should still be preserved once inside
`core_attributes.accessories.source_text`. It does not need to remain duplicated
in `source_specific_attributes` after successful mapping because the new typed
field already keeps exact traceability.

If the source payload does not contain `Příslušenství:`, normalization should
emit the default empty `NormalizedAccessories` value.

## Parser Provenance And Fallback

Accessories parsing should use a dedicated normalization parser implementation
versioned in code as `accessories-v1`. As with nearby places, this parser
version does not require a separate record-level metadata field because the
record already carries the overall `normalization_version`.

The parser should be conservative:

- Supported deterministic tokens populate typed fields and remain out of
  overflow.
- Ambiguous or low-frequency fragments such as `2 garáže` should remain in
  `unparsed_fragments` until the project explicitly approves a garage-specific
  contract field.
- Future unsupported tokens should also land in `unparsed_fragments` rather
  than inventing ad hoc keys or overloading existing counts.
- If parsing partially succeeds, preserve `source_text`, keep the parsed typed
  values, and append only the unresolved fragments to `unparsed_fragments`.

This fallback preserves traceability while avoiding false precision for
accessory semantics that are not yet stable enough for the canonical contract.

## Contract Version Impact

Adding `core_attributes.accessories` is an additive schema change to the
canonical normalized record. The follow-up implementation task should therefore
bump the normalization contract from `normalized-listing-v5` to
`normalized-listing-v6` and update tests and persisted artifact expectations
accordingly.
