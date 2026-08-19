---
name: start-sprint
description: Start a planned sprint in a Workbench project, transitioning its status to ACTIVE.
side_effect: write
---

# Start Sprint

## Intent: start-sprint
### User request patterns
- start sprint
- make sprint active
- make sprint to active
- activate sprint
- begin the active sprint
- launch sprint
- bắt đầu sprint
- kích hoạt sprint

### Retrieval tags
- workbench
- start-sprint
- active-sprint
- sprint-lifecycle
- agile

### Instructions
- **Input Verification Rule**:
  - If `project_id` is unknown, run `python skills/workbench/show_project_overview/scripts/show_project_overview.py` to list projects and ask user to clarify.
  - If `sprint_id` is unknown or unspecified, run `python skills/workbench/get_sprints/scripts/get_sprints.py --project-id <UUID>` to list planned sprints and ask user which sprint to start.
- **Mandatory User Confirmation & Turn Boundary**:
  - Before executing `start_sprint.py`, **ALWAYS** present a clear preview:
    - **Project**: `<project name>`
    - **Sprint Name**: `<sprint name>`
    - **Dates**: `<start date> to <end date>`
    - **Action**: `Transition status to ACTIVE`
  - Ask the user: *"Do you confirm starting sprint '[Sprint Name]' in project '[Project Name]'?"*.
  - **STOP and wait for explicit user confirmation** (e.g. "yes", "confirm", "đồng ý") in a subsequent turn before executing. **DO NOT execute the script in the same turn as the confirmation question.**
- `project_id` and `sprint_id` are required and must be valid UUIDs.

### Required arguments
- `project_id`: UUID of the project.
- `sprint_id`: UUID of the sprint to start.

### Execution
```text
python skills/workbench/start_sprint/scripts/start_sprint.py --project-id <UUID> --sprint-id <UUID>
```
