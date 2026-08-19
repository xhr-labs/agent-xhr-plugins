---
name: workbench-get-task-status-meta
description: Retrieve valid Workbench task status metadata before choosing a task status UUID for creation or updates. Use when the user asks which task statuses exist or when another Workbench task flow needs concrete task status values.
---

# Get Task Status Meta

Use this executable helper when the user needs valid Workbench task status metadata before creating a Workbench task or choosing a task-status UUID.

# Intent Map

## Intent: list-valid-workbench-task-status-metadata
### User request patterns
- show available Workbench task statuses
- what task statuses can I use?
- get valid task status ids
- list task status metadata for task creation
- resolve the right task status value

### Retrieval tags
- workbench
- task
- status
- metadata
- lookup

### Answer objective
Return valid Workbench task status metadata so downstream task flows can use concrete task-status UUIDs.

### Instructions
- Use this helper before task-create or task-update flows when the valid task status values are not yet clear.
- Keep task status names, ids, keys, and types visible whenever the helper returns them.
- Prefer this helper over guessing task status values from informal labels.
- When another flow needs a confirmed task status, tell the user to choose the exact `status_id` from `task_statuses`.

### Supported arguments
- None.

### Execution
- Script entrypoint: `skills/workbench/get_task_status_meta/scripts/get_task_status_meta.py`
- Use the restricted command-style `exec` surface with the explicit runtime-relative wrapper path and CLI flags when available.
