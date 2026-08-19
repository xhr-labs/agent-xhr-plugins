---
name: attendance-approve-timesheet-request
description: Approve an attendance timesheet request by request ID. Use when the user wants to approve a pending timesheet request and the agent should execute skills/attendance/approve_timesheet_request/scripts/approve_timesheet_request.py.
---

# Approve timesheet request

This file is an executable leaf skill entrypoint.

## Runtime entrypoint
- Execute `skills/attendance/approve_timesheet_request/scripts/approve_timesheet_request.py`.
- Do not search for another child skill under this directory.

## Intent Map

### User request patterns
- approve this timesheet request
- approve the pending attendance request
- approve timesheet request tsr-123
- confirm this submitted timesheet
- accept the timesheet correction request
- approve my pending timesheet request
- approve timesheet request
- Approve all pending time attendance requests

### Retrieval tags
- attendance
- timesheet
- approve
- pending
- request-id

### Answer objective
Approve a pending timesheet request by using a concrete timesheet request ID from user input or prior tool output.

### Instructions
- Use CLI flags for normal execution; the final JSON-object tail exists only as temporary compatibility.
- `timesheetRequestId` is required for the final approve action.
- Prefer request IDs returned by tool output instead of guessing from display text.
- If the user does not provide a concrete `timesheetRequestId`, first resolve it from the listing flow.
- For that listing step, prefer `--recursive true` so all matching pending requests are fetched before selecting the final request ID.
- If the user mentions a specific working date or date range, carry that into the listing step with `--start-date <YYYY-MM-DD>` and/or `--end-date <YYYY-MM-DD>` so the candidate set stays narrow.
- For self-referential wording like `my`, `mine`, or `my pending request`, run `python skills/attendance/get_timesheet_requests/scripts/get_timesheet_requests.py --mine true --statuses PENDING --recursive true` and add date flags when the user mentioned them.
- For another employee with an explicit employee ID, run `python skills/attendance/get_timesheet_requests/scripts/get_timesheet_requests.py --employee-ids <employee-id> --statuses PENDING --recursive true` and add date flags when the user mentioned them.
- For another employee named by text instead of ID, first run `python skills/employee/search_employees/scripts/search_employees.py --name "<employee name or keyword>"`, keep the resolved employee ID visible, then run `python skills/attendance/get_timesheet_requests/scripts/get_timesheet_requests.py --employee-ids <employee-id> --statuses PENDING --recursive true` and add date flags when the user mentioned them.
- Only approve a request that is currently in `PENDING` status according to tool output.
- Preserve a user-provided approval note exactly when one is given.
- Do not fabricate approval success; rely on tool output.
- Do not mention internal tool names in the user-facing reply.
- If the user asks to approve all pending attendance requests, first resolve the full pending set with `python skills/attendance/get_timesheet_requests/scripts/get_timesheet_requests.py --statuses PENDING --recursive true` (or add `--mine true` / `--employee-ids` / date flags when the user scope requires it), then approve each returned request ID one by one using this leaf; do not guess or skip IDs.

### Supported arguments
- `timesheetRequestId` — required final request ID for approval.
- `note` — optional approval note.
- `mine` — optional boolean for self-scoped resolution flow before the final approve action.

### Execution
```text
python skills/attendance/approve_timesheet_request/scripts/approve_timesheet_request.py --timesheet-request-id <required id> [--note "<optional string>"] [--mine <optional true|false>]
```
