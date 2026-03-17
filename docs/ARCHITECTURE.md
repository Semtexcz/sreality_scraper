# Architecture

## Purpose

`scraperweb` is a small Python application for:

- scraping apartment sale listings from `sreality.cz`
- enriching listing data with geocoding and postcode lookups
- sending normalized records to a local API endpoint
- loading reference town and district datasets into MongoDB

## Runtime Shape

The project is intentionally split into four top-level areas:

- `scraperweb/`: importable application modules
- `scripts/`: thin executable wrappers
- `data/`: CSV source datasets
- `docs/`: technical documentation and generated API docs

## Main Flows

### Estate scraping flow

1. `scraperweb.estate_scraper` builds runtime configuration from environment.
2. Listing pages are fetched from `sreality.cz`.
3. Estate detail pages are parsed into dictionaries.
4. Address data is geocoded via `geopy`.
5. Postcode-to-district mapping is resolved from MongoDB collection `Okresy`.
6. Final payload is posted to the configured API endpoint.

### Reference data loading flow

1. `scraperweb.towns` reads city datasets from `data/`.
2. `scraperweb.districts_loader` reads postcode coordinates from `data/souradnice.csv`.
3. Records are inserted into MongoDB collections used by the scraper runtime.

## Configuration

Runtime configuration is centralized in `scraperweb.config` and uses:

- `MONGODB_URI`
- `MONGODB_DATABASE`
- `SCRAPER_API_URL`
- `GEOPY_USER_AGENT`

## Constraints

- Scraping depends on external HTML structure at `sreality.cz`.
- Geocoding depends on external service availability and rate limits.
- Full verification requires MongoDB and a receiving API service.
