# Task 007: Build Typer CLI

## Status

backlog

## Goal

Provide a clean operator-facing CLI built with `typer`.

## Scope

- add `typer` as the command-line framework
- create a top-level CLI application with explicit commands for scraping and auxiliary data loading
- support runtime options such as region selection, page limits, item limits, and storage backend selection
- provide help text and argument validation that reflect the raw-data-only scope
- replace or retire legacy entrypoints that no longer fit the target interface

## Notes

The CLI should be thin and delegate work to application services. Command functions should parse input, construct runtime dependencies, and call the orchestrating layer without embedding scraping logic.

## Verification

- `poetry run scraperweb --help` exposes the new Typer-based interface
- scraper commands accept bounded runtime options
- invalid CLI input returns clear validation errors
