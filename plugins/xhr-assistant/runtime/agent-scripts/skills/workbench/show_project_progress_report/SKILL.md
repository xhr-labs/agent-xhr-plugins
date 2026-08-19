---
name: show-project-progress-report
description: Retrieve project progress, sprint reports, burndown, velocity, and spent-time summaries.
side_effect: read
---

# Show Project Progress Report

## Intent: show-project-progress-report
### User request patterns
- show project progress report
- sprint burndown and velocity report
- view project time and task completion summary

### Retrieval tags
- workbench
- project-report
- sprint-report
- burndown
- velocity
- progress-summary

### Instructions
- `project_id` is required and must be a valid UUID.
- `sprint_id`: Provide to retrieve sprint-specific burndown and completion insights.
- `from_date` / `to_date`: Filter date range for project-wide summary.

### Required arguments
- `project_id`: UUID of the project.

### Optional arguments
- `sprint_id`: UUID of the sprint.
- `from_date`: Start date (`YYYY-MM-DD`).
- `to_date`: End date (`YYYY-MM-DD`).

### Execution
```text
python skills/workbench/show_project_progress_report/scripts/show_project_progress_report.py --project-id <UUID> [--sprint-id <UUID>]
```
