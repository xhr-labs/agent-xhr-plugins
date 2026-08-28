---
name: workbench-get-status-latest
description: Fetch the latest Workbench status records for one or more known task IDs. Use when the user asks for the current status of specific tasks and the task IDs are already known.
---

# Get Status Latest

Use this executable leaf when the user wants the current or latest status for known task IDs.

# Intent Map

## Intent: get-latest-status-for-known-tasks
### User request patterns
- show the latest status for task 123
- what is the current status of these tasks?
- fetch the newest status records for these task ids
- get task status for known ids
- check the latest status of task abc

### Retrieval tags
- workbench
- status
- task
- latest

### Answer objective
Return the latest Workbench status for the requested task IDs while preserving the mapping between each task ID and its current status.

### Instructions
- Require one or more concrete `task_id` values before execution.
- If task IDs are missing, use another task-listing leaf first to identify candidates.
- Preserve the mapping between each requested task ID and the returned status.
- Do not invent task IDs.
- Use the executable leaf instead of fabricating status data.

### Required arguments
- `task_id` — one task id or a repeated list of task ids.

### Execution
- Script entrypoint: `skills/workbench/get_status_latest/scripts/get_status_latest.py`
- Use the restricted command-style `exec` surface with the explicit runtime-relative wrapper path and CLI flags when available.
