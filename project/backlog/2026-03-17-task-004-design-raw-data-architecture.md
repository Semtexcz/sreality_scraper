# Task 004: Design Raw Data Architecture

## Status

backlog

## Goal

Define a target architecture that matches the raw-data-only scope and creates a safe base for the refactor.

## Scope

- define clear application layers for CLI, orchestration, scraping, parsing, and persistence
- identify class responsibilities and boundaries according to SOLID principles
- define the raw record contract that must be preserved without enrichment or normalization
- document which current modules are transitional and should be retired after the refactor

## Notes

The current implementation mixes HTTP access, HTML parsing, geocoding, MongoDB access, and API submission in one procedural flow. This task should produce the architectural target that guides the remaining implementation tasks and reduces refactor risk.

## Verification

- architecture documentation describes module boundaries and core classes
- the raw data contract is documented and does not include derived fields
