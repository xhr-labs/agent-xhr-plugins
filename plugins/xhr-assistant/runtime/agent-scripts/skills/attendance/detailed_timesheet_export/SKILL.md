---
name: attendance-detailed-timesheet-export
description: Fetch exhaustive detailed timesheet rows for one explicitly resolved employee and date range, with validation against identity, paging, totals, and potentially truncated notes. Use when the user asks to export or review every detailed timesheet note.
side_effect: read
---

# Detailed timesheet export

This file is an executable leaf skill entrypoint.

## Runtime entrypoint
- Execute `skills/attendance/detailed_timesheet_export/scripts/detailed_timesheet_export.py`.
- Do not search for another child skill under this directory.

## Intent Map

### User request patterns
- export detailed timesheet
- get every single detailed note
- export all timesheet notes for an employee
- full timesheet detail for employee in a month
- detailed attendance export with date, hours, from, to, note
- why is the attendance export missing days
- compare timesheet report total with detailed rows

### Retrieval tags
- attendance
- timesheet
- detailed-export
- notes
- full-list
- validation
- employee-id
- paging

### Answer objective
Return an exhaustive, identity-safe list of timesheet request rows for one explicitly resolved employee and date range. The result is suitable for the agent to present as a table or convert into a spreadsheet.

### Instructions
- Use this leaf instead of `attendance_reports` when the user asks for detailed rows, detailed notes, or export-style data.
- Do not use fuzzy name or email matching directly with this leaf. If the user gives a name, email, or employee code, first resolve the person through `skills/employee/search_employees/scripts/search_employees.py --name "<keyword>"`.
- The employee search script supports `--name` only. Do not call it with `--query`, `--email`, or positional arguments.
- If employee search returns `NO_MATCHES`, try at most one more user-provided identifier from the same request, then stop and ask for an exact employee identifier. Do not keep retrying guessed name fragments and do not fall back to the signed-in user.
- If employee search returns more than one plausible employee, ask the user to choose. Do not guess.
- Pass exactly one `employeeId` after resolving the employee. This avoids mixing one person's rows with another person's rows.
- Always provide an explicit date range. For month requests, use the first and last date of that month.
- The script always fetches recursively with a large page size and returns paging metadata.
- Present `employeeVerification` in the answer so the user can see which employee was exported.
- Review `validation` before answering:
  - If `identityMismatchCount` is greater than zero, warn that the backend returned rows for another employee and that those rows were excluded.
  - If `hasNext` is true, warn that the result may still be incomplete.
  - If `expectedMinutes` was provided and `matchesExpectedMinutes` is false, warn that detailed rows do not match the expected summary total.
  - If `truncatedNoteCount` is greater than zero, state which dates have notes that appear truncated exactly as returned by xHR.
- If the user asks for an `.xlsx` or CSV, create it from the returned `rows`. Do not claim it is an official xHR export unless the backend provides a native export file.

### Required arguments
- `employeeId`: the resolved xHR employee UUID.
- `startDate`: inclusive start date in `YYYY-MM-DD`.
- `endDate`: inclusive end date in `YYYY-MM-DD`.

### Optional arguments
- `statuses`: repeated request statuses. Supported values: `PENDING`, `APPROVED`, `REJECTED`, `CANCELED`. Defaults to `PENDING`.
- `expectedMinutes`: expected total minutes from a summary/report, used for validation.
- `expectedHours`: expected total hours from a summary/report, used for validation when `expectedMinutes` is omitted.
- `sort`: sort string. Defaults to `entryDate,asc`.

### Execution
Run the detailed timesheet export script via the restricted command-style exec surface:

```text
python skills/attendance/detailed_timesheet_export/scripts/detailed_timesheet_export.py --employee-id <employee-id> --start-date <YYYY-MM-DD> --end-date <YYYY-MM-DD> [--statuses <status>]... [--expected-minutes <minutes>] [--expected-hours <hours>] [--sort "<field,direction>"]
```
