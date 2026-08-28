---
name: assign-tasks-to-sprint
description: Move tasks into a sprint or remove tasks from a sprint back to the backlog.
side_effect: write
---

# Assign Tasks to Sprint

## Intent: assign-tasks-to-sprint
### User request patterns
- add task to sprint
- move tasks into sprint
- remove task from sprint
- return task to backlog

### Retrieval tags
- workbench
- assign-sprint
- move-task-sprint
- sprint-backlog
- sprint-planning

### Instructions
- **Input Verification Rule (NEVER guess or select all tasks)**:
  - If the user did not specify which task(s) to move (e.g. user just said "add task to sprint"), **DO NOT guess, assume, or automatically select all tasks in the project**. Run `python skills/workbench/get_tasks/scripts/get_tasks.py --project-id <UUID> --status "open" --page-number 0` to list available tasks and ask the user: *"Which task(s) would you like to add to the sprint?"*.
  - If `sprint_id` is unknown or unspecified, run `python skills/workbench/get_sprints/scripts/get_sprints.py --project-id <UUID>` to list active/planned sprints and ask the user to clarify which sprint to target.
  - If `project_id` is unknown, run `python skills/workbench/show_project_overview/scripts/show_project_overview.py` to list projects and ask the user to clarify.
- **Mandatory User Confirmation & Turn Boundary**:
  - Before calling `assign_tasks_to_sprint.py`, **ALWAYS** present a clear preview of the planned action:
    - **Project**: `<project name>`
    - **Target Sprint**: `<sprint name>`
    - **Tasks**: `<list of task numbers & names>`
    - **Action**: `Add to sprint` (or `Remove to backlog`)
  - Ask the user: *"Do you confirm moving these task(s) into [Sprint Name]?"*.
  - **STOP and wait for explicit user confirmation** (e.g. "yes", "confirm", "đồng ý") in a subsequent user turn. **DO NOT execute the script in the same turn as the confirmation question.**
- `project_id` and `sprint_id` are required and must be valid UUIDs.
- `task_id` can be specified multiple times for bulk assignment (if only task names are known, run `python skills/workbench/get_tasks/scripts/get_tasks.py --name "<task title or keyword>" --page-number 0` to resolve task UUIDs).
- `action` defaults to `add` (move into sprint). Set to `remove` to return tasks to the backlog.

### Required arguments
- `project_id`: UUID of the project.
- `sprint_id`: UUID of the target sprint.
- `task_id`: UUID of the task to add or remove (repeat `--task-id <UUID>` for multiple).

### Optional arguments
- `action`: `add` (default) or `remove`.

### Execution
```text
python skills/workbench/assign_tasks_to_sprint/scripts/assign_tasks_to_sprint.py --project-id <UUID> --sprint-id <UUID> --task-id <UUID> [--action <add|remove>]
```

