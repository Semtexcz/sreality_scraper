# Project Tracking

This directory mirrors the lightweight task-tracking structure used in `Bookvoice`.

## Layout

- `project/backlog/`: planned work that has not been completed yet
- `project/done/`: completed tasks kept as a historical record

## Task File Convention

Recommended file naming:

`YYYY-MM-DD-task-XXX-short-description.md`

Each task file should use this structure:

```md
---
task: TASK-015
status: "backlog"
priority: P1
type: feature
---

# Short task title

Task: TASK-015
Status: backlog
Priority: P1
Type: feature
Author:
Created: 2026-02-21
Related:

## Problem

Describe the problem the task solves.

## Definition of Done

- [ ] Add clear completion criteria.

## Notes

- Add implementation guidance, constraints, or dependencies.
```

Recommended fields:

- `task`: stable task identifier
- `status`: `backlog`, `in_progress`, `done`, or other explicit workflow state
- `priority`: for example `P1`, `P2`, `P3`
- `type`: for example `feature`, `refactor`, `test`, `design`, `docs`

When a task is finished, move it from `project/backlog/` to `project/done/`.
