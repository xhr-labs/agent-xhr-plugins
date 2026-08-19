---
name: complete-sprint
description: Complete/close an active sprint in a Workbench project, optionally moving open tasks to another sprint or backlog.
side_effect: write
---

# Complete Sprint

## Intent: complete-sprint
### User request patterns
- complete sprint
- close sprint
- finish active sprint

### Retrieval tags
- workbench
- complete-sprint
- close-sprint
- sprint-lifecycle
- backlog-rollover

### Instructions
- **Input Verification & Destination Prompt**:
  - `project_id` and `sprint_id` are required and must be valid UUIDs.
  - If `project_id` is unknown, run `python skills/workbench/show_project_overview/scripts/show_project_overview.py` to list projects and ask user to clarify.
  - If `sprint_id` is unknown, run `python skills/workbench/get_sprints/scripts/get_sprints.py --project-id <UUID>` to find the active sprint ID.
  - **Incomplete tasks destination**: Explicitly ask the user whether incomplete tasks should move to the **Backlog** (default) or to another **Sprint**:
    - If moving to another sprint and the user provides a sprint name, run `python skills/workbench/get_sprints/scripts/get_sprints.py --project-id <UUID>` to resolve the target `sprint_id`, then pass `--move-to-sprint-id <UUID>`.
    - If moving to Backlog, omit `--move-to-sprint-id`.
- **Mandatory User Confirmation & Turn Boundary**:
  - Before executing `complete_sprint.py`, **ALWAYS** present a clear preview:
    - **Project**: `<project name>`
    - **Sprint to Complete**: `<sprint name>`
    - **Incomplete Tasks Destination**: `Backlog` (or `<Target Sprint Name>`)
    - **Action**: `Close sprint and rollover open tasks`
  - Ask the user: *"Do you confirm completing sprint '[Sprint Name]' with rollover to [Destination]?"*.
  - **STOP and wait for explicit user confirmation** (e.g. "yes", "confirm", "đồng ý") in a subsequent turn before executing. **DO NOT execute the script in the same turn as the confirmation question.**

### Required arguments
- `project_id`: UUID of the project.
- `sprint_id`: UUID of the sprint to complete.

### Optional arguments
- `move_to_sprint_id`: UUID of the next sprint to move uncompleted tasks to (defaults to backlog).

### Execution
```text
python skills/workbench/complete_sprint/scripts/complete_sprint.py --project-id <UUID> --sprint-id <UUID> [--move-to-sprint-id <UUID>]
```
