---
name: attendance-get-timesheet-requests
description: List attendance timesheet requests with optional caller, employee, date-range, status, paging, recursive, and sort filters. Use when the user wants to review or search timesheet requests and the agent should execute skills/attendance/get_timesheet_requests/scripts/get_timesheet_requests.py.
---

# Get timesheet requests

This file is an executable leaf skill entrypoint.

## Runtime entrypoint
- Execute `skills/attendance/get_timesheet_requests/scripts/get_timesheet_requests.py`.
- Do not search for another child skill under this directory.

## Intent Map

### User request patterns
- show timesheet requests
- list pending timesheet requests
- get attendance requests for this employee
- show me submitted timesheets waiting for approval
- list timesheet requests from 2026-04-01 to 2026-04-07
- find attendance requests with status pending
- show attendance records that need review
- check submitted timesheets for employee emp-1
- show my timesheet requests
- list my pending attendance requests
- show me my pending timesheet requests
- show pending timesheet requests of all employee

### Retrieval tags
- attendance
- timesheet
- requests
- approvals
- list
- filter

### Answer objective
Return attendance timesheet requests filtered by caller, employee, date range, status, paging, or sort settings, including the caller's own requests when the intent is personal request lookup.

### Instructions
- Extract any employee, date-range, status, paging, or sort filters the user already provided.
- Decide employee scope explicitly:
  - If the user is asking about their own requests with wording like `I`, `my`, `my timesheet requests`, or `assigned to me`-style self reference, pass `mine=true`.
  - If the user is asking about another employee and gives a name or ambiguous person reference instead of an employee ID, first run `python skills/employee/search_employees/scripts/search_employees.py --name "<employee name or keyword>"`, keep the resolved employee ID visible, and then pass `--employee-ids <employee-id>` into this leaf.
  - If the user is asking about another employee and already provides explicit employee IDs, pass `employeeIds` directly instead of using `mine=true`.
  - If explicit `employeeIds` are already available, let them take precedence over `mine=true`.
- `mine=true` means the app layer should fall back to the current user's `xhr-employee-id` when no explicit `employeeIds` are provided.
- If the user does not provide a date range, the application defaults `startDate` to the first day of the month from three months ago and `endDate` to today.
- Treat `recursive` as optional and default-off.
- Do not pass `recursive=true` unless the user or the current workflow explicitly needs an exhaustive multi-page result set.
- When `recursive=true`, default `size` to `1000` unless the user explicitly asked for another page size.
- Pay attention to the returned `meta` block, especially `page_number`, `page_size`, `has_next`, `pages_fetched`, and `total_items_returned`, so you know whether more pages existed and how much data was collected.
- Valid `statuses` values for this leaf are: `PENDING`, `APPROVED`, `REJECTED`, `CANCELED`.
- Use the tool output as the source of truth for request IDs and statuses.
- Do not mention internal tool names in the user-facing reply.

### Supported arguments
- `page` — optional result page number.
- `size` — optional page size, default `20`, or `1000` by default when `recursive=true`.
- `recursive` — optional boolean, default `false`. When `true`, keep fetching pages until `meta.has_next` is `false`.
- `mine` — optional boolean. When `true` and `employeeIds` are not provided, the helper falls back to the current user's `xhr-employee-id`.
- `employeeIds` — optional repeated employee-id filter.
- `startDate` — optional start date in `YYYY-MM-DD` format.
- `endDate` — optional end date in `YYYY-MM-DD` format.
- `statuses` — optional repeated request-status filter. Supported values: `PENDING`, `APPROVED`, `REJECTED`, `CANCELED`.
- `sort` — optional sort string.

### Execution
Run the attendance get-timesheet-requests script via the restricted command-style exec surface:

```text
python skills/attendance/get_timesheet_requests/scripts/get_timesheet_requests.py [--employee-ids <optional id>]... [--start-date <optional YYYY-MM-DD>] [--end-date <optional YYYY-MM-DD>] [--statuses <optional status>]... [--page <optional number>] [--size <optional number>] [--sort "<optional string>"] [--mine <optional true|false>] [--recursive <optional true|false>]
```

If no filters are needed, run the script without any extra flags:

```text
python skills/attendance/get_timesheet_requests/scripts/get_timesheet_requests.py
```
