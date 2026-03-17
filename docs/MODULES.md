# Modules

## Package Modules

### `scraperweb.config`

Centralized runtime settings and path helpers.

### `scraperweb.estate_scraper`

Primary scraping workflow for downloading raw estate listings from `sreality.cz` and
persisting them without transformation.

### `scraperweb.towns`

Loader for regional towns, district towns, and towns with extended competence.

### `scraperweb.districts_loader`

Loader for postcode and district reference data from `data/souradnice.csv`.

### Compatibility wrappers

These modules exist to preserve the old import surface while delegating to the refactored implementation:

- `scraperweb.main`
- `scraperweb.cities_data`
- `scraperweb.districts`

## Script Entry Points

- `scripts/scrape_estates.py`
- `scripts/load_towns.py`
- `scripts/load_districts.py`

Poetry also exposes:

- `scraperweb`
- `scraperweb-load-towns`
- `scraperweb-load-districts`
