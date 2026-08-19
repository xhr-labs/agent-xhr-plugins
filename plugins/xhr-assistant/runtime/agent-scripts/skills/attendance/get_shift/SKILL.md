---
name: attendance-get-shift
description: Find attendance shifts by id, exact name, or search keyword using GET /v1/atd/shifts. Use when the user wants to look up a shift before assigning employees, editing settings, or validating a shift exists.
---

# Get shift

This file is an executable leaf skill entrypoint.

## Runtime entrypoint
- Execute `skills/attendance/get_shift/scripts/get_shift.py`.
- Do not search for another child skill under this directory.

## Intent Map

### User request patterns
- find shift night-shift
- get shift by name main-shift
- look up shift by id
- search attendance shifts
- find active shift named sandbox
- list shifts matching keyword night

### Retrieval tags
- attendance
- shift
- search
- lookup
- read-action

### Answer objective
Retrieve shifts from `/v1/atd/shifts` and surface exact matches clearly.

### Instructions
- Prefer `shift_id` when provided.
- If `shift_name` is provided, send it as `search_keyword` and then perform exact-name filtering client-side.
- `search_keyword` is optional and can be used for fuzzy lookup.
- Default pagination:
  - `page=0`
  - `size=20`
- `sort` is optional. Do not send it unless the caller explicitly needs it.
- Do not claim an exact match unless it appears in `exact_matches`.

### Arguments
- `shift_id` (optional)
- `shift_name` (optional)
- `search_keyword` (optional)
- `is_active` (optional)
- `page` (optional)
- `size` (optional)
- `sort` (optional)

### Execution
```text
python skills/attendance/get_shift/scripts/get_shift.py [--shift-id <id>] [--shift-name <name>] [--search-keyword <keyword>] [--is-active <true|false>] [--page <int>] [--size <int>] [--sort <field,(asc|desc)>]
```
