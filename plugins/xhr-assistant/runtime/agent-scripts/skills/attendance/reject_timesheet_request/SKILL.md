---
name: attendance-reject-timesheet-request
description: Reject an attendance timesheet request by request ID, with an optional reason. Use when the user wants to reject a pending timesheet request and the agent should execute skills/attendance/reject_timesheet_request/scripts/reject_timesheet_request.py.
---

# Reject timesheet request

This file is an executable leaf skill entrypoint.

## Runtime entrypoint
- Execute `skills/attendance/reject_timesheet_request/scripts/reject_timesheet_request.py`.
- Do not search for another child skill under this directory.

## Intent Map

### User request patterns
- reject this timesheet request
- reject the pending attendance request
- reject timesheet request tsr-123
- decline this submitted timesheet
- reject the timesheet correction request with reason late submission
- reject my pending timesheet request
- cancel this timesheet request
- reject timesheet request

### Retrieval tags
- attendance
- timesheet
- reject
- cancel
- pending
- request-id

### Answer objective
Reject a pending timesheet request by using a concrete timesheet request ID from user input or prior tool output.

### Instructions
- Use CLI flags for normal execution; the final JSON-object tail exists only as temporary compatibility.
- `timesheetRequestId` is required for the final reject action.
- Prefer request IDs returned by tool output instead of guessing from display text.
- If the user does not provide a concrete `timesheetRequestId`, first resolve it from the listing flow.
- For that listing step, prefer `--recursive true` so all matching pending requests are fetched before selecting the final request ID.
- If the user mentions a specific working date or date range, carry that into the listing step with `--start-date <YYYY-MM-DD>` and/or `--end-date <YYYY-MM-DD>` so the candidate set stays narrow.
- For self-referential wording like `my`, `mine`, or `my pending request`, run `python skills/attendance/get_timesheet_requests/scripts/get_timesheet_requests.py --mine true --statuses PENDING --recursive true` and add date flags when the user mentioned them.
- For another employee with an explicit employee ID, run `python skills/attendance/get_timesheet_requests/scripts/get_timesheet_requests.py --employee-ids <employee-id> --statuses PENDING --recursive true` and add date flags when the user mentioned them.
- For another employee named by text instead of ID, first run `python skills/employee/search_employees/scripts/search_employees.py --name "<employee name or keyword>"`, keep the resolved employee ID visible, then run `python skills/attendance/get_timesheet_requests/scripts/get_timesheet_requests.py --employee-ids <employee-id> --statuses PENDING --recursive true` and add date flags when the user mentioned them.
- Only reject a request that is currently in `PENDING` status according to tool output.
- Preserve a user-provided rejection `reason` exactly when one is given.
- Do not fabricate rejection success; rely on tool output.
- Do not mention internal tool names in the user-facing reply.

### Supported arguments
- `timesheetRequestId` — required final request ID for rejection.
- `reason` — optional rejection reason.
- `mine` — optional boolean for self-scoped resolution flow before the final reject action.

### Execution
```text
python skills/attendance/reject_timesheet_request/scripts/reject_timesheet_request.py --timesheet-request-id <required id> [--reason "<optional string>"] [--mine <optional true|false>]
```
