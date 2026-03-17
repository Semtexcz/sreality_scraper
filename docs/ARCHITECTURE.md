# Architecture

## Purpose

`scraperweb` is a Python application for:

- downloading raw listing data from `sreality.cz`
- preserving the downloaded content without modifying the payload
- keeping the persistence layer simple and replaceable

The project goal is raw data acquisition. Data transformations, enrichment, or
business-level normalization are outside the intended scope of the scraper itself.

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
3. Estate detail pages are downloaded and parsed into a raw machine-readable form.
4. The captured records are stored without additional data operations.

The storage target is intentionally not fixed yet. The current design direction should
support either of these backends:

- MongoDB for document-oriented raw record storage
- filesystem storage for raw JSON or HTML snapshots

### Reference data loading flow

1. `scraperweb.towns` reads city datasets from `data/`.
2. `scraperweb.districts_loader` reads postcode coordinates from `data/souradnice.csv`.
3. Records are prepared for auxiliary use when the selected storage or runtime model
   requires them.

## Configuration

Runtime configuration is centralized in `scraperweb.config` and uses:

- `MONGODB_URI`
- `MONGODB_DATABASE`
- `SCRAPER_API_URL`
- `GEOPY_USER_AGENT`

Some of these variables belong to the current implementation and may become obsolete as
the project is reduced to raw extraction and storage only.

## Constraints

- Scraping depends on external HTML structure at `sreality.cz`.
- The scraper should avoid mutating source data during capture.
- The final persistence decision between MongoDB and filesystem storage is still open.
