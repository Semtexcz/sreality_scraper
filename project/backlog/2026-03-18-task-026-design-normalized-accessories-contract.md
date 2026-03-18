---
task: TASK-026
status: "backlog"
priority: P1
type: design
---

# Design normalized accessories contract

Task: TASK-026
Status: backlog
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

- [ ] Define a typed normalized accessories contract with explicit ownership and
      field names.
- [ ] Decide which recurring tokens should map to booleans, which should map to
      enums, and which should map to numeric area or count fields.
- [ ] Define how repeated area-bearing features such as balcony, loggia,
      terrace, and cellar should be represented.
- [ ] Define fallback handling for rare or ambiguous tokens such as
      `2 garáže` or any future unexpected accessory strings.
- [ ] Document whether the original `Příslušenství:` text remains preserved as
      `source_text`, overflow, or both.

## Notes

- Current data analysis found 457 records with `Příslušenství:`.
- Frequent boolean or enum-like tokens include `Výtah`, `Bez výtahu`,
  `Bezbariérový přístup`, `Nemá bezbariérový přístup`, `Zařízeno`,
  `Částečně zařízeno`, and `Nezařízeno`.
- Frequent quantifiable tokens include `Balkon o ploše Xm²`,
  `Lodžie o ploše Xm²`, `Terasa o ploše Xm²`, `Sklep o ploše Xm²`, and
  `Parkovací stání s N místy`.
