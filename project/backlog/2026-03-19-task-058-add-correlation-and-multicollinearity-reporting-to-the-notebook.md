---
task: TASK-058
status: "backlog"
priority: P2
type: feature
---

# Add correlation and multicollinearity reporting to the notebook

Task: TASK-058
Status: backlog
Priority: P2
Type: feature
Author:
Created: 2026-03-19
Related: TASK-054, TASK-055

## Problem

The article needs a visual correlation map and a clear explanation of which
predictors move together, but the repository does not yet provide a supported
workflow for distinguishing ordinary correlation with price from
multicollinearity among the predictors themselves.

## Definition of Done

- [ ] Add a notebook workflow that computes and visualizes correlations between
      numeric predictors and the supported price targets.
- [ ] Include a graphical correlation map suitable for article use.
- [ ] Add explicit multicollinearity checks, such as pairwise screening and a
      more formal diagnostic for selected numeric features.
- [ ] Summarize the main mutually dependent feature groups and any proposed
      reduction or grouping strategy for later training.
- [ ] Document where categorical fields require different treatment than simple
      numeric correlation coefficients.

## Notes

- The notebook should analyze both `asking_price_czk` and
  `price_per_square_meter_czk` where that distinction changes interpretation.
- The output should help decide which predictors remain in the later production
  training stage.
- Favor visuals and diagnostics that are easy to explain in the blog article.
