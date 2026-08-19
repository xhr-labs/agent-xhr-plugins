---
name: update-task
description: Update an existing Workbench task's title, description, status, priority, assignee, reporter, dates, sprint, or story points.
side_effect: write
---

# Update Task

## Intent: update-task
### User request patterns
- update task
- change task status to In Progress / Done
- reassign task to an employee
- change task priority or due date
- update task description or story points

### Retrieval tags
- workbench
- update-task
- task-status
- assignee
- priority
- due-date
- edit-task

### Instructions
- **Input Verification Rule**:
  - `task_id` is required and must be a valid UUID. If only task number/name is known, run `python skills/workbench/get_tasks/scripts/get_tasks.py --name "<task title or keyword>" --page-number 0` to resolve `task_id`.
  - If the user did not specify which task to update, run `python skills/workbench/get_tasks/scripts/get_tasks.py --page-number 0` and ask the user to clarify.
  - At least one field to update must be provided.
- **Mandatory User Confirmation & Turn Boundary**:
  - Before executing `update_task.py`, **ALWAYS** present a clear preview of the planned changes:
    - **Task**: `<task number & task name>`
    - **Proposed Changes**: `<list of updated fields and their new values>`
  - Ask the user: *"Do you confirm updating task '[Task Name]' with these changes?"*.
  - **STOP and wait for explicit user confirmation** (e.g. "yes", "confirm", "đồng ý") in a subsequent turn before executing. **DO NOT execute the script in the same turn as presenting the preview.**
- `priority` must be one of `Low`, `Medium`, `High`, `Urgent`.
- `status_id` must be a valid task status UUID (resolve via `get_task_status_meta` if status name is provided).
- `assignee_id` / `reporter_id` must be valid employee UUIDs (or aliases `--assignee` / `--reporter`).

### Required arguments
- `task_id`: UUID of the task to update.

### Optional arguments
- `task_name`: New task title/name.
- `description`: New task description text.
- `status_id`: UUID of the target task status.
- `priority`: Priority level (`Low`, `Medium`, `High`, `Urgent`).
- `assignee_id`: UUID of the assigned employee (or empty string to unassign).
- `reporter_id`: UUID of the reporter employee.
- `start_date`: Start date (`YYYY-MM-DD`).
- `due_date`: Due date (`YYYY-MM-DD`).
- `project_id`: UUID of project (if moving project).
- `sprint_id`: UUID of sprint (or empty string to move to backlog).
- `story_point`: Story points integer.

### Execution
```text
python skills/workbench/update_task/scripts/update_task.py --task-id <UUID> [--task-name "<name>"] [--status-id <UUID>] [--priority <Low|Medium|High|Urgent>] [--assignee-id <UUID>] [--due-date <YYYY-MM-DD>]
```
