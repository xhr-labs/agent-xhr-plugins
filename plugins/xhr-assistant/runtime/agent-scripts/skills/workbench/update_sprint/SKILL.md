---
name: update-sprint
description: Update sprint details including name, goal, start/end dates, or duration in a Workbench project.
side_effect: write
---

# Update Sprint

## Intent: update-sprint
### User request patterns
- update sprint
- change sprint goal or dates
- rename sprint

### Retrieval tags
- workbench
- update-sprint
- edit-sprint
- sprint-dates
- sprint-goal

### Instructions
- **Input Verification Rule**:
  - `project_id` and `sprint_id` are required and must be valid UUIDs.
  - If unknown, run `python skills/workbench/show_project_overview/scripts/show_project_overview.py` for project, and `python skills/workbench/get_sprints/scripts/get_sprints.py --project-id <UUID>` for sprint ID.
  - At least one field to update must be provided.
- **Mandatory User Confirmation & Turn Boundary**:
  - Before executing `update_sprint.py`, **ALWAYS** present a clear preview:
    - **Project**: `<project name>`
    - **Sprint Name**: `<sprint name>`
    - **Proposed Changes**: `<list fields to change and new values>`
  - Ask the user: *"Do you confirm updating sprint '[Sprint Name]' with these changes?"*.
  - **STOP and wait for explicit user confirmation** (e.g. "yes", "confirm", "đồng ý") in a subsequent turn before executing. **DO NOT execute the script in the same turn as the confirmation question.**

### Required arguments
- `project_id`: UUID of the project.
- `sprint_id`: UUID of the sprint to update.

### Optional arguments
- `sprint_name`: New name of the sprint.
- `goal`: New sprint goal description.
- `start_date`: Start date (`YYYY-MM-DD`).
- `end_date`: End date (`YYYY-MM-DD`).
- `duration`: Duration descriptor.

### Execution
```text
python skills/workbench/update_sprint/scripts/update_sprint.py --project-id <UUID> --sprint-id <UUID> [--sprint-name "<name>"] [--goal "<goal>"] [--start-date <YYYY-MM-DD>] [--end-date <YYYY-MM-DD>]
```
