---
name: attendance-submit-timesheets
description: Submit attendance timesheets for an employee with one or more dated entries. Use when the user wants to submit timesheet entries and the agent should execute skills/attendance/submit_timesheets/scripts/submit_timesheets.py after the final entry details are confirmed.
---

# Submit timesheets

This file is an executable leaf skill entrypoint.

## Runtime entrypoint
- Execute `skills/attendance/submit_timesheets/scripts/submit_timesheets.py`.
- Do not search for another child skill under this directory.

## Intent Map

### User request patterns
- submit my timesheet for today
- submit attendance for employee emp-1
- log work hours from 09:00 to 18:00 on 2026-04-09
- submit timesheet entries for this week
- create a timesheet entry for 2026-04-09 from 08:30 to 17:30
- submit these attendance entries
- send my work log for approval
- Help me submit timesheet
- Help me submit timesheet 2025-12-30, 08:00, 17:00, 60 2025-12-31, 08:00, 17:00, 60
- Help me submit timesheet
  2025-12-30, 08:00, 17:00, 60
  2025-12-31, 08:00, 17:00, 60

### Retrieval tags
- attendance
- timesheet
- submit
- work-log
- write-action

### Answer objective
Submit one or more attendance timesheet entries for the target employee after the final entry details are confirmed.

### Instructions
- Use CLI flags for normal execution; the final JSON-object tail exists only as temporary compatibility.
- `employeeId` is required, but do not ask the user for employee ID.
- Resolve employee scope from the initial request before execution:
  - If the initial request mentions any employee explicitly, including an employee name, keyword, or employee ID, treat that as an other-employee flow and resolve the target through `python skills/employee/search_employees/scripts/search_employees.py --name "<employee name or keyword or provided employee reference>"`, then use the resolved employee ID for `employeeId`.
  - If the initial request does not mention any employee explicitly, default to the current user and use the current `xhr-employee-id` as `employeeId`.
- Do not ask the user whether to use self or another employee when the initial request already determines the scope.
- `entriesJson` must be a JSON array of one or more objects.
- For every record in `entriesJson`, require all four fields before execution: `date`, `start_time`, `end_time`, `break_duration_minutes`.
- Never execute with partial records. If any record is missing one of those fields, ask the user for the missing values first.
- Preserve the exact entry dates, times, and break minutes the user confirmed.
- If the user provides multiline timesheet rows in the form `YYYY-MM-DD, HH:MM, HH:MM, break_minutes`, parse each line into an `entriesJson` object with `date`, `start_time`, `end_time`, and `break_duration_minutes` before execution.
- Before execution, the LLM must show the user a clear per-record summary of the final `entriesJson` contents using user-friendly labels, including `date`, `start_time`, `end_time`, and `break_duration_minutes` for each record.
- This leaf performs a write action. Get explicit user confirmation after showing the final employee and per-record entry details, and only then execute.
- Do not fabricate submission success; rely on tool output.
- Do not mention internal tool names in the user-facing reply.

### Required arguments
- `employeeId` — required employee ID.
- `entriesJson` — required JSON array of timesheet entries.

### Scope helpers
- If the initial request names or references any employee explicitly, resolve `employeeId` through `search_employees` without asking the user for employee ID.
- If the initial request does not identify any employee, resolve `employeeId` from the current `xhr-employee-id`.

### Execution
```text
python skills/attendance/submit_timesheets/scripts/submit_timesheets.py --employee-id <required employee id> --entries-json '<required JSON array>'
```
