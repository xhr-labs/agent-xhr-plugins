---
name: workbench-get-overdue-tasks
description: List overdue Workbench tasks with optional paging, assignee, priority, and status filters. Use when the user asks about overdue work, late tasks, or delayed items in Workbench.
---

# Get Overdue Tasks

Use this executable leaf when the user wants overdue tasks.

# Intent Map

## Intent: list-overdue-workbench-tasks
### User request patterns
- show overdue tasks
- what tasks are late?
- list delayed work items
- show my overdue tasks
- get overdue tasks in Workbench
- Overdue tasks from all spaces?
- Do I have overdue tasks?
- How many time the due date has not been met

### Retrieval tags
- workbench
- tasks
- overdue
- list

### Answer objective
Return overdue Workbench tasks with any requested filters applied so the user can review what is late.

### Instructions
- Use this leaf when the user asks for overdue tasks or delayed work.
- Carry forward any paging, assignee, priority, or status filters the user already provided.
- If the user names a status informally and the valid status metadata is unclear, use `get_status_meta` first.
- Prefer the narrowest valid filter set that matches the request.
- Use the executable leaf rather than inventing overdue-task data.

### Supported arguments
- `page_number` — optional result page number.
- `page_size` — optional page size.
- `priorities` — optional repeated priority filter.
- `status_id` — optional repeated status-id filter.
- `status_key` — optional repeated status-key filter.
- `status_name` — optional repeated status-name filter.
- `assignee_id` — optional repeated assignee-id filter.

### Execution
- Script entrypoint: `skills/workbench/get_overdue_tasks/scripts/get_overdue_tasks.py`
- Example current-user execution: `python skills/workbench/get_overdue_tasks/scripts/get_overdue_tasks.py --mine true --page-number 0`
- Example other-employee execution: `python skills/workbench/get_overdue_tasks/scripts/get_overdue_tasks.py --assignee-id <employee-id> --page-number 0`
- Example project-scoped execution: `python skills/workbench/get_overdue_tasks/scripts/get_overdue_tasks.py --project-id <project-id> --page-number 0`
- Example all-visible execution: `python skills/workbench/get_overdue_tasks/scripts/get_overdue_tasks.py --page-number 0`
- Use the restricted command-style `exec` surface with the explicit runtime-relative wrapper path and CLI flags when available.
