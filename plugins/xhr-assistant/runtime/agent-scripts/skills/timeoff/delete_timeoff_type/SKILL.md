---
name: delete-timeoff-type
description: Permanently delete a time-off type after explicit user confirmation.
side_effect: write
---

# Delete Time-Off Type

## Intent: delete-timeoff-type
### User request patterns
- delete leave type
- remove time off type

### Retrieval tags
- timeoff
- delete-type
- remove-leave-type

### Instructions
- **Input Verification Rule**:
  - `type_id` is required and must be a valid UUID (if unknown, run `python skills/timeoff/get_timeoff_types/scripts/get_timeoff_types.py` to resolve).
- **Mandatory Deletion Warning & Turn Boundary**:
  - Deleting a leave type is destructive. **ALWAYS** show the deletion warning:
    - **Type ID / Name**: `<type_id>`
    - **Warning**: *"Deleting this time-off type will remove it from the company setup. This action cannot be undone."*
  - Ask the user: *"Are you sure you want to permanently delete this time-off type?"*.
  - **STOP and wait for explicit user confirmation** in a subsequent turn before executing. **DO NOT execute the script in the same turn as presenting the warning.**

### Required arguments
- `type_id`: UUID of the leave type to delete.

### Execution
```text
python skills/timeoff/delete_timeoff_type/scripts/delete_timeoff_type.py --type-id <UUID>
```
