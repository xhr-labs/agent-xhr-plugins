---
name: get-sprints
description: Retrieve the list of sprints (active, planned, completed) for a Workbench project.
side_effect: read
---

# Get Sprints

## Intent: get-sprints
### User request patterns
- show sprints for project
- list sprints
- view active sprint and backlog sprints

### Retrieval tags
- workbench
- sprints
- sprint-list
- sprint-planning
- active-sprint

### Instructions
- `project_id` is required and must be a valid UUID (if only project name is known, resolve `project_id` via `show_project_overview` first).
- Returns sprints grouped into `active_sprints`, `planned_sprints`, and `completed_sprints`.

### Required arguments
- `project_id`: UUID of the project.

### Optional arguments
- `include_metrics`: Set to true to include velocity and burndown metrics.

### Execution
```text
python skills/workbench/get_sprints/scripts/get_sprints.py --project-id <UUID>
```
