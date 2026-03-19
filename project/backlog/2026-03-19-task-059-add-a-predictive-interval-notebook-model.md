---
task: TASK-059
status: "backlog"
priority: P1
type: feature
---

# Add a predictive interval notebook model

Task: TASK-059
Status: backlog
Priority: P1
Type: feature
Author:
Created: 2026-03-19
Related: TASK-054, TASK-055, TASK-057, TASK-058

## Problem

The final notebook outcome should estimate a usable market range for a supplied
apartment configuration, but the repository does not yet define or implement a
notebook-stage predictive workflow that returns calibrated lower and upper
bounds rather than a misleading single-point estimate.

## Definition of Done

- [ ] Add a notebook workflow that predicts apartment prices from the approved
      analysis dataset using a clearly documented feature subset.
- [ ] Produce interval-style outputs with lower, central, and upper estimates
      that are suitable for article presentation.
- [ ] Compare at least one interpretable baseline with a stronger nonlinear
      benchmark and justify the recommended first notebook approach.
- [ ] Report validation metrics that explain interval usefulness and major error
      characteristics.
- [ ] Document the notebook-stage limitations and the requirements for turning
      the approach into a later production training workflow.

## Notes

- Favor a prediction range such as `P10-P50-P90` or `P25-P50-P75` over a single
  number.
- The notebook should present the output as an estimated market range derived
  from observed listings, not as a definitive valuation.
- Keep the implementation structured so the later training stage can lift the
  chosen method into a deterministic runtime workflow.
