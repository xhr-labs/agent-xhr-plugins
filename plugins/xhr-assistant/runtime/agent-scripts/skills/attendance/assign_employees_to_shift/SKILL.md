---
name: attendance-assign-employees-to-shift
description: Assign one or more employees to an attendance shift using shift_id or exact shift_name resolution plus direct employee_ids and/or exact employee_names resolution. Use when the user wants to add employees into a shift and needs clear failure reasons for missing or ambiguous names before executing the assignment.
---

# Assign employees to shift

This file is an executable leaf skill entrypoint.

## Runtime entrypoint
- Execute `skills/attendance/assign_employees_to_shift/scripts/assign_employees_to_shift.py`.
- Do not search for another child skill under this directory.

## Intent Map

### User request patterns
- assign employee to shift
- add employees to night-shift
- assign Alice and Bob to main-shift
- add employee ids to a shift
- assign employees to attendance shift by shift name
- attach employees into sandbox shift

### Retrieval tags
- attendance
- shift
- employee
- assignment
- write-action

### Answer objective
Assign employees to `/v1/atd/shifts/{shift_id}/employees` after resolving shift and employee inputs safely.

### Instructions
- This leaf performs a write action. Get explicit user confirmation after showing the final assignment summary, and only then execute.
- Require one of:
  - `shift_id`
  - `shift_name`
- Require at least one of:
  - `employee_ids`
  - `employee_names`
- Prefer `shift_id` over `shift_name`.
- If only `shift_name` is provided, call the shared get-shift application flow with `search_keyword=shift_name`, then filter exact name client-side.
- If exact shift-name resolution returns 0 matches, fail clearly.
- If exact shift-name resolution returns more than 1 match, fail clearly and do not guess.
- Accept direct `employee_ids` as-is.
- For each `employee_name`, call the shared employee search flow, then keep only exact name matches client-side.
- If an employee name resolves to 0 matches, fail clearly for that name.
- If an employee name resolves to more than 1 exact match, fail clearly for that name and do not guess.
- Merge direct `employee_ids` with resolved employee ids and deduplicate before assignment.
- Do not fabricate success; rely on tool output.
- Do not mention internal tool names in the user-facing reply.

### Required arguments
- one of `shift_id` or `shift_name`
- at least one of `employee_ids` or `employee_names`

### Execution
```text
python skills/attendance/assign_employees_to_shift/scripts/assign_employees_to_shift.py [--shift-id <id>] [--shift-name <name>] [--employee-id <id> ...] [--employee-name <name> ...]
```
