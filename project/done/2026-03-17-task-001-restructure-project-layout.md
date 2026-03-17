# Task 001: Restructure Project Layout

## Status

done

## Goal

Align the repository with a clearer top-level structure inspired by `Bookvoice`.

## Completed Work

- moved CSV datasets into `data/`
- moved generated HTML documentation into `docs/api/`
- introduced dedicated runtime modules for scraping and data loading
- added script wrappers in `scripts/`
- added central environment-based configuration
- preserved old module entrypoints through compatibility wrappers

## Verification

- `python3 -m compileall scraperweb scripts`

## Notes

Full runtime verification against live services was not executed as part of the structural refactor.
