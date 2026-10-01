---
name: update-timeoff-type
description: Update an existing time-off leave type's name, color, or requirement settings.
side_effect: write
---

# Update Time-Off Type

## Intent: update-timeoff-type
### User request patterns
- update leave type
- rename time off type
- change leave type settings

### Retrieval tags
- timeoff
- update-type
- edit-leave-type

### Instructions
- **Input Verification Rule**:
  - `type_id` is required and must be a valid UUID (if unknown, run `python skills/timeoff/get_timeoff_types/scripts/get_timeoff_types.py` to resolve).
  - At least one field to update must be specified.
- **Mandatory User Confirmation & Turn Boundary**:
  - Before executing `update_timeoff_type.py`, **ALWAYS** present a preview of changes.
  - Ask the user: *"Do you confirm updating this time-off type?"*.
  - **STOP and wait for explicit user confirmation** in a subsequent turn before executing. **DO NOT execute the script in the same turn as presenting the preview.**

### Required arguments
- `type_id`: UUID of the leave type to update.

### Optional arguments
- `name`: New name.
- `color`: New hex color.
- `is_paid`: Paid status.
- `requires_attachment`: Attachment requirement flag.
- `requires_reason`: Reason requirement flag.

### Execution
```text
python skills/timeoff/update_timeoff_type/scripts/update_timeoff_type.py --type-id <UUID> [--name "<name>"] [--color "<hex>"]
```
