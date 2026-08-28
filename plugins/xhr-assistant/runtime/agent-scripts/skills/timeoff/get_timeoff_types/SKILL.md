---
name: timeoff-get-timeoff-types
description: List time off types when a concrete time-off type ID is needed for submission or validation. Use when the user provides a leave-type name, asks what leave types exist, or needs to resolve a type ID.
---

# Get Time Off Types

Use this executable leaf when the user provides a leave-type name but the flow needs a concrete `time_off_type_id`.

# Intent Map

## Intent: list-or-resolve-timeoff-types
### User request patterns
- show available leave types
- show time off types
- find the annual leave id
- find the type id for sick leave
- resolve the time off type id

### Retrieval tags
- timeoff
- leave-types
- type-id
- lookup

### Answer objective
Return available time-off types and help resolve a human leave-type name to the concrete `time_off_type_id` needed by downstream actions.

### Instructions
- Use this leaf when a submission or validation flow needs a concrete type ID.
- Keep both display names and IDs visible in the final answer whenever possible.
- If the user named a specific leave type, highlight the best matching type ID instead of dumping an unstructured list.
- Use pagination arguments only when needed.
- Pair this with submission flows when the type ID is not already known.

### Supported arguments
- `page` — optional page number.
- `size` — optional page size.

### Execution
- Script entrypoint: `skills/timeoff/get_timeoff_types/scripts/get_timeoff_types.py`
- Use the restricted command-style `exec` surface with the explicit runtime-relative wrapper path and CLI flags when available.
