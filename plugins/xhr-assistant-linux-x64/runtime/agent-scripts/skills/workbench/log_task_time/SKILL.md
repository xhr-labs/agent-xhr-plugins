---
name: log-task-time
description: Log spent work time against a Workbench task with flexible duration, work date, and notes.
side_effect: write
---

# Log Task Time

## Intent: log-task-time
### User request patterns
- log 2 hours on task
- log time for this task
- record spent time on task

### Retrieval tags
- workbench
- log-time
- timesheet
- spent-time
- time-tracking

### Instructions
- **Input Verification Rule**:
  - `task_id` is required and must be a valid UUID. If only a task name or keyword is provided, run `python skills/workbench/get_tasks/scripts/get_tasks.py --name "<task title or keyword>" --page-number 0` to resolve `task_id`.
  - If task is unspecified, run `python skills/workbench/get_tasks/scripts/get_tasks.py --mine true --page-number 0` and ask user to specify the task.
  - Note: In Workbench PM, work time can only be logged against tasks assigned to the current employee. If the task is unassigned or assigned to someone else, guide the user to assign the task first.
  - `duration` is required and supports flexible duration formats: `2h`, `1h 30m`, `90m`, `0.5d`, `120` (minutes).
- **Mandatory User Confirmation & Turn Boundary**:
  - Before executing `log_task_time.py`, **ALWAYS** present a preview:
    - **Task**: `<task number & task name>`
    - **Date**: `<YYYY-MM-DD>`
    - **Duration**: `<duration>`
    - **Notes**: `<notes or "None">`
  - Ask the user: *"Do you confirm logging [Duration] on task '[Task Name]'?"*.
  - **STOP and wait for explicit user confirmation** (e.g. "yes", "confirm", "đồng ý") in a subsequent turn before executing. **DO NOT execute the script in the same turn as presenting the preview.**
- `work_date` defaults to today (`YYYY-MM-DD`).
- `notes` is optional work description.

### Required arguments
- `task_id`: UUID of the task.
- `duration`: Duration string (e.g. `2h`, `1h 30m`, `90m`, `120`).

### Optional arguments
- `work_date`: Work date (`YYYY-MM-DD`, default today).
- `notes`: Work note / description.

### Execution
```text
python skills/workbench/log_task_time/scripts/log_task_time.py --task-id <UUID> --duration "<duration>" [--work-date <YYYY-MM-DD>] [--notes "<notes>"]
```
