---
name: timeoff-get-leave-request
description: List or inspect leave requests with optional status, employee, and date-range filters. Use when the user asks about leave history, leave status, pending requests, or finding a request by time window.
---

# Get Leave Request

Use this executable leaf when the user needs leave-request history, status checks, or request lookup.

# Intent Map

## Intent: list-or-filter-leave-requests
### User request patterns
- Who in the company is on leave today?
- Who is out today?
- Which of my leave requests were rejected?
- Find all pending leave requests this week.
- Who will be out next week?
- Who will be out tomorrow?
- Show me my leave requests
- my leave requests
- Team upcoming leaves
- My upcoming leaves
- leave request
- time-off requests
- find the leave request I can cancel
- show leave requests that can still be cancelled
- find the request id for the leave I want to cancel
- list cancellable leave requests
- find the leave request I can withdraw

### Retrieval tags
- timeoff
- leave-request
- history
- status

### Answer objective
Return the user's leave requests or a filtered subset, preserving request IDs and statuses so the result can support follow-up actions.

### Instructions
- Extract any status, employee, or date-range filters the user already provided.
- Valid `status` values are `PENDING`, `APPROVED`, `CANCELLED`, and `REJECTED`, and the search may include multiple statuses at once such as `PENDING,APPROVED`.
- When the user asks who is on leave today, who is out today, who will be out tomorrow, who will be out next week, or similar availability questions, default the `status` filter to `APPROVED` unless the user explicitly asks for another status.
- If the user does not provide a time range, default `from_date` to today and `to_date` to the end of next year.
- When the user wants to find a request to cancel but does not know the request ID, use this leaf to find the matching request first, default the `status` filter to `PENDING`, default `from_date` to today, default `to_date` to the end of next year, and keep cancellable request IDs visible in the answer.
- Prefer the narrowest valid filter set so the result is useful for follow-up actions like approve or cancel.
- Use `page` and `size` when the user asks for pagination.
- Treat `recursive` as optional and default-off.
- Do not pass `recursive=true` unless the user or the current workflow explicitly requires fetching all pages or an exhaustive result set.
- When `recursive=true`, default `size` to `1000` unless the user explicitly asked for another page size.
- Keep request IDs visible in the final answer whenever the script returns them.
- Pay attention to the returned `meta` block, especially `page`, `size`, `has_next`, `pages_fetched`, and `total_items_returned`, so you know whether another fetch is needed and how much data was collected.
- Decide employee scope explicitly:
  - If the user is asking about their own leave with wording like `I`, `my`, `my leave`, `my requests`, or another clearly self-referential phrasing, pass `mine=true`.
  - If the user is asking about another employee, resolve or pass that employee's `employee_id` instead of using `mine=true`.
  - If an explicit `employee_id` is already available, let that explicit `employee_id` take precedence.
- `mine=true` means the app layer should fall back to the current user's `xhr-employee-id` when no explicit `employee_id` is provided.
- If the user asks about another employee, only pass `employee_id` when policy and authorization allow it.
- If the user wants a specific employee's leave requests but does not know the `employee_id`, resolve it first from the employee name by running `python skills/employee/search_employees/scripts/search_employees.py --name "<required name or keyword>"`.
- Use the executable leaf command rather than inventing request data.

### Supported arguments
- `status` — optional request status filter. Valid values: `PENDING`, `APPROVED`, `CANCELLED`, `REJECTED`. Multiple values may be provided together, for example `PENDING,APPROVED`.
- `employee_id` — optional employee id when the user asks about another employee and policy allows it.
- `mine` — optional boolean. When `true` and `employee_id` is not provided, the helper falls back to the current user's `xhr-employee-id`.
- `from_date` — optional start date in `YYYY-MM-DD`.
- `to_date` — optional end date in `YYYY-MM-DD`.
- `page` — optional page number, default `0`.
- `size` — optional page size, default `20`, or `1000` by default when `recursive=true`.
- `recursive` — optional boolean, default `false`. When `true`, keep fetching pages until `meta.has_next` is `false`.

### Execution
- Script entrypoint: `skills/timeoff/get_leave_request/scripts/get_leave_request.py`
- Example paginated execution: `python skills/timeoff/get_leave_request/scripts/get_leave_request.py --status PENDING --from-date YYYY-MM-DD --to-date YYYY-MM-DD --page 0 --size 20`
- Example caller-leave execution: `python skills/timeoff/get_leave_request/scripts/get_leave_request.py --mine true --status PENDING --from-date YYYY-MM-DD --to-date YYYY-MM-DD`
- Example recursive execution: `python skills/timeoff/get_leave_request/scripts/get_leave_request.py --status APPROVED --from-date YYYY-MM-DD --to-date YYYY-MM-DD --recursive true`
- Use the restricted command-style `exec` surface with the explicit runtime-relative wrapper path and CLI flags when available.
