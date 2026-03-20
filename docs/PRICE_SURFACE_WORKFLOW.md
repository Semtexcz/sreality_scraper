# Price Surface Workflow

## Purpose

This document defines the first supported repository workflow for generating a
map-ready apartment price surface and its companion uncertainty outputs from
listing-level observations.

The design is intentionally conservative. The repository should first ship a
workflow that is replayable from persisted artifacts, interpretable to readers,
and explicit about where location quality or sample density is too weak to
support a strong spatial claim.

## Scope

The workflow is designed for:

- notebook-backed analytical storytelling
- article-quality scalar price maps
- deterministic replay from persisted repository artifacts
- later promotion into production training and scoring contracts

The workflow is not designed to:

- infer street-level values where only municipality-level or district-level
  coordinates exist
- hide sparse coverage behind visually smooth interpolation
- replace later predictive-model outputs with a map-only heuristic

## Design Decision

The first supported workflow should use deterministic grid aggregation over the
approved enriched or analysis-dataset records, with a robust per-cell summary
value and explicit uncertainty outputs.

Approved first workflow:

1. start from the canonical analysis dataset defined after `raw ->
   normalized -> enriched -> modeling` lineage
2. filter to records that satisfy the approved notebook data-quality rules
3. include only records with coordinates precise enough to support the selected
   grid resolution
4. assign each included listing to one approved spatial grid cell
5. aggregate `price_per_square_meter_czk` per cell using the median as the
   primary scalar value
6. publish explicit uncertainty fields alongside the scalar value
7. suppress or label cells that do not meet minimum support thresholds

The approved first scalar output is therefore a discrete grid-cell field, not a
continuous interpolated surface.

## Why Grid Aggregation Comes First

Grid aggregation is the best fit for the repository's current constraints.

### Replayability

- it depends only on persisted coordinates, approved spatial-grid identifiers,
  and deterministic summary statistics
- the same input records always produce the same cell outputs without random
  initialization or optimization drift
- the result can be versioned as a small tabular artifact rather than a
  notebook-only rendering side effect

### Interpretability

- each scalar value can be explained as a robust summary of the listings inside
  one explicit cell
- support thresholds, inclusion rules, and uncertainty labels can be audited at
  the cell level
- the workflow does not imply spatial precision beyond the best available
  coordinate precision

### Data Requirements

- it remains viable with moderate listing counts
- it tolerates irregular geographic coverage better than local regression
- it works directly with the deterministic square-grid hierarchy already owned
  by enrichment

## Candidate Approach Comparison

### Grid Aggregation

Summary:

- aggregate observed listing values inside approved spatial cells

Strengths:

- highest replayability
- simple to explain and validate
- compatible with mixed but explicit coordinate precision rules
- natural fit for uncertainty sidecars such as cell count and price spread

Weaknesses:

- introduces visible cell boundaries
- can look sparse in low-coverage areas
- does not estimate values for unobserved locations

Repository decision:

- approved as the first supported workflow

### Kernel Smoothing

Summary:

- estimate a continuous field by weighting nearby listings around each output
  location

Strengths:

- visually smooth map output
- can reduce hard cell-boundary artifacts
- can summarize local trends when point coverage is dense and precise

Weaknesses:

- more sensitive to bandwidth selection and edge effects
- harder to defend when coordinates are coarse or mixed in precision
- can imply false certainty in sparse areas unless uncertainty controls are
  unusually explicit
- requires extra design choices for evaluation points, kernel family, and
  coarse-geocode weighting

Repository decision:

- not approved as the first supported workflow
- may be explored later as a notebook appendix once the grid workflow is
  implemented and can act as the auditable baseline

### Spatial Regression Or Trend-Surface Modeling

Summary:

- fit a model that predicts price from coordinates and possibly other features,
  then score locations across a map

Strengths:

- can combine spatial structure with other explanatory variables
- can produce a full predicted field and associated model residual analysis
- may become useful in later production workflows

Weaknesses:

- weakest interpretability for the first map artifact
- requires stronger assumptions, more design surface, and clearer separation
  between observed-market summaries and modeled predictions
- depends on the still-pending notebook dataset, feature-selection, and model
  decisions

Repository decision:

- explicitly deferred until after the exploratory notebook and production-model
  design tasks

## Input Contract And Staged Dependencies

The price-surface workflow must not consume raw or normalized artifacts
directly.

Required staged dependencies:

1. `TASK-053` defines the canonical analysis dataset contract
2. `TASK-054` implements deterministic export of that dataset
3. `TASK-055` adds the reproducible notebook scaffold that consumes the export
4. `TASK-056` implements this approved grid workflow in notebook form

The workflow consumes only approved downstream fields:

- `listing_id`
- `captured_at_utc`
- `price_per_square_meter_czk`
- resolved coordinate values
- geocoding source, confidence, and precision fields
- approved spatial grid identifiers
- administrative hierarchy fields needed for reporting and filtering

## Coordinate Precision And Inclusion Rules

Coordinate precision must affect both inclusion and uncertainty. The workflow
must not render all coordinate sources as equally trustworthy.

Approved precision-aware policy for the first implementation:

- `listing` precision coordinates are fully eligible for the canonical rendered
  grid resolution
- `street` precision coordinates may be included only when the selected grid
  resolution is coarse enough that the positional uncertainty is materially
  smaller than the cell size
- `district` or `municipality` precision coordinates are excluded from the
  canonical cell-level scalar map
- unresolved coordinates are excluded entirely

Approved confidence-aware policy:

- high-confidence deterministic coordinates are included at full weight
- lower-confidence but still resolved coordinates may remain eligible only when
  the notebook documents that policy explicitly
- the first supported workflow should prefer hard inclusion rules over complex
  fractional weighting so the output remains auditable

This means the first implementation should bias toward exclusion plus explicit
coverage reporting rather than down-weighting coarse coordinates into the main
surface silently.

## Weighting Policy

The first supported workflow should use equal listing weight inside each cell.

Not approved for the first implementation:

- distance-weighted within-cell aggregation
- confidence-based fractional listing weights
- target-derived post-stratification adjustments

Rationale:

- equal weighting keeps the scalar value interpretable as a direct summary of
  observed listings
- coordinate quality is easier to defend through inclusion rules and uncertainty
  flags than through opaque fractional weights

## Primary Scalar Output

The primary price-surface value per cell is:

- `median_price_per_square_meter_czk`

The median is preferred over the mean because:

- asking-price data can be heavy-tailed
- local samples may be small in the first notebook workflow
- the median is easier to explain as a robust central tendency measure

Optional companion descriptive statistics may also be emitted when supported by
cell size:

- mean price per square meter
- lower and upper quartiles
- minimum and maximum observed values

These are secondary descriptive outputs, not replacements for the canonical
median field.

## Required Uncertainty Outputs

Every rendered or reportable cell must expose explicit uncertainty sidecars.

The first supported workflow requires at least these outputs:

- `listing_count`
- `price_per_square_meter_iqr_czk`
- `coverage_status`

Recommended additional fields:

- `included_listing_share`
- `excluded_low_precision_count`
- `excluded_missing_coordinate_count`
- `coordinate_precision_mix`

Field semantics:

- `listing_count` shows local support and is the minimum required density signal
- `price_per_square_meter_iqr_czk` exposes within-cell dispersion without
  assuming normality
- `coverage_status` makes sparse, suppressed, or precision-limited cells
  machine-readable

The first notebook may also compute a simple uncertainty label such as:

- `supported`
- `sparse`
- `precision_limited`
- `insufficient_data`

## Minimum Support Thresholds

The workflow must define an explicit minimum listing count before a cell is
rendered as part of the canonical scalar map.

Repository decision:

- the exact threshold belongs to the analysis-dataset and notebook
  implementation tasks because it depends on the final export density and
  deduplication rules
- the implementation must use one documented threshold, not an implicit visual
  judgment
- cells below the threshold must remain visible through uncertainty or coverage
  reporting even when their scalar value is suppressed

This design therefore approves the threshold concept and suppression behavior,
while leaving the numeric cutoff to `TASK-056` once the exported dataset is
available for calibration.

## Output Artifacts

The workflow should produce explicit versioned artifacts rather than notebook
state only.

Approved artifact families for the first implementation:

- analysis dataset export artifact owned by the later `TASK-054` workflow
- derived price-surface cell table owned by the notebook workflow
- rendered notebook figures for article or review use

Minimum required columns for the derived cell table:

- `surface_workflow_version`
- `grid_system`
- `grid_resolution`
- `spatial_cell_id`
- `median_price_per_square_meter_czk`
- `listing_count`
- `price_per_square_meter_iqr_czk`
- `coverage_status`
- `included_coordinate_precision_levels`
- `analysis_dataset_version`
- `generated_at_utc`

The cell table should be the canonical bridge between notebook calculations and
any later API, export, or production packaging decision.

## Contract Ownership

Ownership remains split by stage:

- enrichment owns coordinates, geocoding quality, and spatial grid identifiers
- the analysis dataset export owns notebook-facing tabular projection
- the price-surface workflow owns cell-level aggregation and uncertainty
  summaries

This task does not introduce a new runtime package yet. It approves the
workflow and artifact contract that later notebook and production tasks should
implement.

## Implementation Guidance For TASK-056

`TASK-056` should:

- load the canonical exported analysis dataset rather than reflattening
  artifacts ad hoc
- document the exact precision filter and minimum support threshold used
- aggregate to one approved grid resolution first, with optional comparison
  views only as secondary outputs
- emit the required uncertainty columns with every map-ready cell record
- suppress scalar values for unsupported cells while still reporting coverage
  diagnostics
- keep any optional smoothing experiments clearly labeled as exploratory and
  outside the canonical supported workflow
