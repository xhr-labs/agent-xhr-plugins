---
name: manage-custom-fields
description: List available custom fields or set custom field values on Workbench tasks.
side_effect: write
---

# Manage Custom Fields

## Intent: manage-custom-fields
### User request patterns
- show custom fields
- set custom field value on task
- view task custom attributes

### Retrieval tags
- workbench
- custom-fields
- task-fields
- custom-attributes
- field-values

### Instructions
- **Input Verification Rule**:
  - `action`: `list` (default) or `set` (set field value on task).
  - When setting a value, `task_id`, `field_id`, and `value` are required (if only task name is known, run `python skills/workbench/get_tasks/scripts/get_tasks.py --name "<task title or keyword>" --page-number 0` to resolve `task_id`).
- **Mandatory User Confirmation & Turn Boundary (for action set)**:
  - Setting custom field values is a write action. Before executing `manage_custom_fields.py --action set`, **ALWAYS** present a preview:
    - **Task**: `<task number & name>`
    - **Custom Field**: `<field name or ID>`
    - **New Value**: `<value>`
  - Ask the user: *"Do you confirm setting this custom field value on task '[Task Name]'?"*.
  - **STOP and wait for explicit user confirmation** (e.g. "yes", "confirm", "đồng ý") in a subsequent turn before executing. **DO NOT execute the script in the same turn as presenting the preview.**

### Required arguments
- None (when listing fields).

### Optional arguments
- `action`: `list` | `set`.
- `project_id`: UUID of project (for filtering available custom fields).
- `task_id`: UUID of task.
- `field_id`: UUID of the custom field.
- `value`: Value to assign to the custom field.

### Execution
```text
python skills/workbench/manage_custom_fields/scripts/manage_custom_fields.py [--project-id <UUID>] [--task-id <UUID>] [--action set] [--field-id <UUID>] [--value "<value>"]
```
