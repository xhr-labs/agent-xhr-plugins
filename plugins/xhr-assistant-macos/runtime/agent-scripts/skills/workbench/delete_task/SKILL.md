---
name: delete-task
description: Permanently delete a Workbench task by its ID after explicit user confirmation.
side_effect: write
---

# Delete Task

## Intent: delete-task
### User request patterns
- delete task
- remove task from project
- delete this workbench task

### Retrieval tags
- workbench
- delete-task
- remove-task
- task-management

### Instructions
- **Input Verification Rule**:
  - `task_id` is required and must be a valid UUID. If only task number/name is known, run `python skills/workbench/get_tasks/scripts/get_tasks.py --name "<task title or keyword>" --page-number 0` to resolve `task_id`.
  - If the user did not specify which task to delete, run `python skills/workbench/get_tasks/scripts/get_tasks.py --page-number 0` and ask the user to clarify.
- **Mandatory Deletion Warning & Turn Boundary**:
  - Task deletion is a destructive write action. **ALWAYS** show the deletion warning first:
    - **Task**: `<task number & task name> (<task UUID>)`
    - **Warning**: *"This action is permanent and cannot be undone."*
  - Ask the user: *"Are you sure you want to permanently delete task '[Task Name]'?"*.
  - **STOP and wait for explicit user confirmation** (e.g. "yes", "delete it", "xóa") in a subsequent turn before executing. **DO NOT execute the delete script in the same turn as presenting the warning.**

### Required arguments
- `task_id`: UUID of the task to delete.

### Optional arguments
- `task_name`: Task name for user-facing confirmation clarity.
- `confirmed`: Explicit confirmation flag (`true` to proceed with deletion).

### Execution
```text
python skills/workbench/delete_task/scripts/delete_task.py --task-id <UUID> [--task-name "<name>"] --confirmed true
```
