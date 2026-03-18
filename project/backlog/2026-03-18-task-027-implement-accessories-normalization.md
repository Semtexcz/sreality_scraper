---
task: TASK-027
status: "backlog"
priority: P1
type: feature
---

# Implement accessories normalization

Task: TASK-027
Status: backlog
Priority: P1
Type: feature
Author:
Created: 2026-03-18
Related: TASK-026

## Problem

After the accessories contract is defined, normalization should parse the
source-backed `Příslušenství:` field into explicit typed facts instead of
forcing downstream consumers to inspect a mixed free-text string. The parser
must remain deterministic and conservative because accessory tokens vary between
simple flags and measured sub-features.

## Definition of Done

- [ ] Implement tokenization for the `Příslušenství:` source text using the
      comma-delimited normalized tail instead of the duplicated leading
      concatenated fragment.
- [ ] Map supported flags, furnishing states, area-bearing features, and
      parking-capacity features into the typed accessories contract.
- [ ] Preserve unsupported or ambiguous accessory fragments in an explicit
      overflow or `unparsed_fragments` field for traceability.
- [ ] Add focused unit tests that cover common combinations and rare edge cases
      such as `Parkovací stání s 4 místy` and `2 garáže`.
- [ ] Update normalization documentation, fixtures, and versioning impacted by
      the contract change.

## Notes

- Favor explicit optional fields over implicit dictionaries with dynamic keys.
- Do not infer amenities from listing title or description text.
