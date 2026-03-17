# scraperweb

`scraperweb` je maly Python projekt pro scraping nabidek bytu ze `sreality.cz` a pomocne nacteni referencnich mest do MongoDB.

## Struktura

- `scraperweb/`: aplikacni kod
- `scripts/`: spousteci skripty
- `data/`: CSV vstupy a pomocna data
- `docs/`: technicka dokumentace a vygenerovane API docs
- `project/`: backlog a historie hotovych ukolu
- `AGENTS.md`: pravidla pro AI agenty a automatizovane prispevatele

## Rychly start

```bash
poetry install
poetry run scraperweb --help
poetry run scraperweb-load-towns --help
poetry run scraperweb-load-districts --help
```

## Konfigurace

Projekt pouziva environment promenne:

- `MONGODB_URI` (default `mongodb://localhost:27017`)
- `MONGODB_DATABASE` (default `RealEstates`)
- `SCRAPER_API_URL` (default `http://localhost:8000/receivedData`)
- `GEOPY_USER_AGENT` (default `scraperweb`)

Priklad:

```bash
export MONGODB_URI="mongodb://localhost:27017"
export MONGODB_DATABASE="RealEstates"
poetry run scraperweb
```
