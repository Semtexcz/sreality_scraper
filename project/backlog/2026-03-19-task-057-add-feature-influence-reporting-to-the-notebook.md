---
task: TASK-057
status: "backlog"
priority: P2
type: feature
---

# Add feature-influence reporting to the notebook

Task: TASK-057
Status: backlog
Priority: P2
Type: feature
Author:
Created: 2026-03-19
Related: TASK-054, TASK-055

## Problem

The notebook should explain the main drivers associated with apartment prices,
but the repository does not yet define how feature influence will be measured,
grouped, and presented without confusing model contribution, pairwise
correlation, and causal interpretation.

## Definition of Done

- [ ] Add a notebook workflow that fits at least one baseline model and one
      stronger benchmark model for factor analysis.
- [ ] Compute feature influence with a method appropriate for the selected model
      family.
- [ ] Group low-level predictors into broader article-facing categories before
      presenting contribution shares.
- [ ] Add a chart-ready output suitable for the planned grouped influence
      visualization, including the requested percentage breakdown if it remains
      statistically defensible.
- [ ] Document interpretation limits so the article does not overstate causal
      claims.

## Notes

- Do not treat simple univariate correlation as a valid measure of influence.
- Keep grouped categories stable enough that later training documentation can
  reuse them.
- The chosen workflow should stay compatible with interval modeling work that
  follows.
