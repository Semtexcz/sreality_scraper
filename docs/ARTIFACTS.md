# Artifacts

## Source-Controlled Inputs

- `data/OkresniMesta.csv`
- `data/ObceSRozsirenouPusobnosti.csv`
- `data/souradnice.csv`

These files are treated as input datasets for reference-data loading.

## Generated Outputs

The repository currently does not define a dedicated output directory for scraper runs.

The intended generated output is raw data downloaded from `sreality.cz` without
post-processing.

The persistence backend is still undecided. Candidate outputs are:

- MongoDB collections containing raw listing records
- filesystem snapshots containing raw JSON or HTML responses

Derived or normalized payloads are not a target artifact for this project scope.

## Generated Documentation

`docs/api/` contains generated HTML documentation from the earlier module layout. It is documentation output, not primary source code.

## Ignored Local Artifacts

The repo ignores local caches and build artifacts such as:

- `__pycache__/`
- `*.pyc`
- virtual environments and local tool caches
