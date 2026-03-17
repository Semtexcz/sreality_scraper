# Task 009: Add Test Coverage for Refactored Runtime

## Status

backlog

## Goal

Create a reliable automated test suite for the refactored architecture and CLI.

## Scope

- add unit tests for scraper clients, parsers, storage adapters, and orchestration services
- add CLI tests for the `typer` commands and argument validation
- add fixture-based tests for representative listing pages and detail pages
- keep tests deterministic and independent from live network services
- verify both filesystem and MongoDB storage behavior where practical

## Notes

This task should validate the new architecture rather than the old procedural implementation. Focus on behavior, explicit contracts, and regression safety during future changes.

## Verification

- `poetry run pytest` passes
- fixtures cover both listing discovery and detail extraction scenarios
- tests prove that persisted records remain raw and unmodified
