---
name: create-timeoff-type
description: Create a new time-off leave type (e.g. Annual Leave, Sick Leave, Paternity Leave) with paid/unpaid and policy settings.
side_effect: write
---

# Create Time-Off Type

## Intent: create-timeoff-type
### User request patterns
- create new leave type
- add time off type
- configure new leave category

### Retrieval tags
- timeoff
- create-type
- leave-type
- timeoff-setup

### Instructions
- **Input Verification Rule**:
  - `name` is required.
  - `color`: Hex color (default `#2563eb`).
  - `is_paid`: Boolean (default `true`).
  - `requires_attachment`: Boolean (default `false`).
  - `requires_reason`: Boolean (default `false`).
- **Mandatory User Confirmation & Turn Boundary**:
  - Before executing `create_timeoff_type.py`, **ALWAYS** present a preview:
    - **Name**: `<name>`
    - **Paid / Unpaid**: `<Paid or Unpaid>`
    - **Color**: `<color>`
    - **Requires Attachment / Reason**: `<Yes/No>`
  - Ask the user: *"Do you confirm creating this time-off type?"*.
  - **STOP and wait for explicit user confirmation** in a subsequent turn before executing. **DO NOT execute the script in the same turn as presenting the preview.**

### Required arguments
- `name`: Name of the leave type.

### Optional arguments
- `code`: Short code identifier.
- `color`: Color hex string (e.g. `#2563eb`).
- `is_paid`: True for paid leave, False for unpaid.
- `requires_attachment`: True if document proof is required.
- `requires_reason`: True if reason text is mandatory.

### Execution
```text
python skills/timeoff/create_timeoff_type/scripts/create_timeoff_type.py --name "<name>" [--code "<code>"] [--color "<hex>"] [--is-paid true|false] [--requires-attachment true|false]
```
