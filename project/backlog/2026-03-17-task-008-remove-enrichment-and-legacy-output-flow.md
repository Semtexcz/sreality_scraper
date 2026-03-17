# Task 008: Remove Enrichment and Legacy Output Flow

## Status

backlog

## Goal

Eliminate behavior that conflicts with the raw-data acquisition objective.

## Scope

- remove geocoding from the scraper runtime path
- remove API posting from the scraper runtime path
- remove or isolate derived-field generation that mutates source records
- simplify configuration to the values required for fetching and raw persistence only
- update documentation to reflect the final runtime behavior after implementation

## Notes

This task should be executed after the new service and storage layers exist. The result should be a scraper that downloads and stores source data, not a pipeline that enriches or transforms it.

## Verification

- runtime execution no longer depends on geocoding or external API delivery
- stored records match the captured source content
- obsolete configuration variables are removed or clearly marked as deprecated
