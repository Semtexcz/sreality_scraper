# Task 005: Refactor Scraper into Services

## Status

backlog

## Goal

Replace the monolithic scraper flow with explicit classes and small services that are easier to test and maintain.

## Scope

- extract HTTP fetching into dedicated client classes
- extract listing-page and detail-page parsing into dedicated parser classes
- add an application service that coordinates page discovery and record collection
- remove hidden coupling between scraping logic and persistence or delivery side effects
- ensure new modules, classes, and functions include docstrings and type hints

## Notes

This refactor should prioritize readability, explicit dependencies, and single-purpose classes. The target is a codebase that a senior Python engineer would recognize as maintainable and reviewable.

## Verification

- scraper workflow can run through the new service layer
- parsing logic is callable without live persistence dependencies
- modules pass static import and compile checks
