# Task 006: Add Raw Storage Abstraction

## Status

backlog

## Goal

Introduce a persistence abstraction for raw records and provide interchangeable storage backends.

## Scope

- define a storage interface for saving raw listing records and optional raw page snapshots
- implement a filesystem-based storage adapter
- implement a MongoDB-based storage adapter
- make storage backend selection configurable without changing scraper code
- document tradeoffs and operational expectations for both backends

## Notes

The scraper should not know whether records are stored in files or in MongoDB. This task is the key separation point that allows the project to evaluate both persistence strategies without rewriting the core flow.

## Verification

- the scraper can persist raw records through either backend
- storage-specific behavior is covered by deterministic tests
- no enrichment or normalization is introduced in stored records
