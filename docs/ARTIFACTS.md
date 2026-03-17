# Artifacts

## Source-Controlled Inputs

- `data/OkresniMesta.csv`
- `data/ObceSRozsirenouPusobnosti.csv`
- `data/souradnice.csv`

These files are treated as input datasets for reference-data loading.

## Generated Outputs

The repository currently does not define a dedicated output directory for scraper runs.

Operational outputs are external to the repo:

- MongoDB collections:
  - `Okresy`
  - `Towns`
- HTTP payloads sent to `SCRAPER_API_URL`

## Generated Documentation

`docs/api/` contains generated HTML documentation from the earlier module layout. It is documentation output, not primary source code.

## Ignored Local Artifacts

The repo ignores local caches and build artifacts such as:

- `__pycache__/`
- `*.pyc`
- virtual environments and local tool caches
