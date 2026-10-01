---
name: attendance-remove-employee-from-shift
description: Remove one or more employees from an attendance shift using shift_id or exact shift_name resolution plus direct employee_ids and/or exact employee_names resolution. Use when the user wants to unassign employees from a shift and needs clear failure reasons for missing or ambiguous names before executing the removal.
---

# Remove employee from shift

This file is an executable leaf skill entrypoint.

## Runtime entrypoint
- Execute `skills/attendance/remove_employee_from_shift/scripts/remove_employee_from_shift.py`.
- Do not search for another child skill under this directory.

## Intent Map

### User request patterns
- remove employee from shift
- unassign employee from sandbox shift
- remove ty from sandbox
- unassign employees from attendance shift
- delete employee assignment from shift

### Retrieval tags
- attendance
- shift
- employee
- assignment
- write-action

### Answer objective
Remove employees from a shift after resolving shift and employee inputs safely.

### Instructions
- This leaf performs a write action. Get explicit user confirmation after showing the final removal summary, and only then execute.
- Require one of:
  - `shift_id`
  - `shift_name`
- Require at least one of:
  - `employee_ids`
  - `employee_names`
- Prefer `shift_id` over `shift_name`.
- If only `shift_name` is provided, resolve attendance app, list active shifts, then filter exact name client-side.
- If exact shift-name resolution returns 0 matches, fail clearly.
- If exact shift-name resolution returns more than 1 match, fail clearly and do not guess.
- Accept direct `employee_ids` as-is.
- For each `employee_name`, call the shared employee search flow, then keep only exact name matches client-side.
- If an employee name resolves to 0 matches, fail clearly for that name.
- If an employee name resolves to more than 1 exact match, fail clearly for that name and do not guess.
- Merge direct `employee_ids` with resolved employee ids and deduplicate before removal.
- Do not fabricate success; rely on tool output.
- Do not mention internal tool names in the user-facing reply.

### Required arguments
- one of `shift_id` or `shift_name`
- at least one of `employee_ids` or `employee_names`

### Execution
```text
python skills/attendance/remove_employee_from_shift/scripts/remove_employee_from_shift.py [--shift-id <id>] [--shift-name <name>] [--employee-id <id> ...] [--employee-name <name> ...]
```
