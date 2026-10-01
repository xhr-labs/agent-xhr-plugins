---
name: timeoff-approve-request
description: Approve a leave request when the target request ID is known. Use when the user asks to approve, confirm, or authorize a leave request.
---

# Approve Leave Request

Use this leaf when the user wants to approve a leave request and the request ID is already known.

# Intent Map

## Intent: approve-confirmed-leave-request
### User request patterns
- approve this leave request
- approve request id abc123
- approve this time off request
- confirm this leave request
- authorize this leave request
- Approve leave request

### Retrieval tags
- timeoff
- approve
- leave-request
- write-action

### Answer objective
Approve the confirmed leave request ID and clearly report which request was approved.

### Instructions
- Require a concrete `request_id` before execution.
- First decide whether the target leave request belongs to the current employee or another employee.
- If the user's wording is personal, such as `my leave request`, `my pending leave`, or another clearly self-referential phrasing, treat the lookup scope as the current employee and use `--mine true` in the helper leave-request lookup.
- If the user is asking about another employee, first resolve that employee by running `python skills/employee/search_employees/scripts/search_employees.py --name "<required name or keyword>"` and keep the resolved `employee_id` visible for the helper leave-request lookup.
- If `request_id` is missing, first use `get_leave_request` to find candidate pending requests and keep the returned ID visible.
- If the user already provided a date or date range, include it in that helper command using `--from-date YYYY-MM-DD --to-date YYYY-MM-DD`.
- If the user did not provide a date or date range, default the helper lookup window to `from_date=today` and `to_date=end of next year`.
- Example helper command for the current employee when dates are known: `python skills/timeoff/get_leave_request/scripts/get_leave_request.py --mine true --status PENDING --from-date YYYY-MM-DD --to-date YYYY-MM-DD`.
- Example helper command for the current employee when dates are not given: `python skills/timeoff/get_leave_request/scripts/get_leave_request.py --mine true --status PENDING --from-date <today> --to-date <end-of-next-year>`.
- Example helper command for another employee when dates are known: `python skills/timeoff/get_leave_request/scripts/get_leave_request.py --employee-id <employee-id> --status PENDING --from-date YYYY-MM-DD --to-date YYYY-MM-DD`.
- Example helper command for another employee when dates are not given: `python skills/timeoff/get_leave_request/scripts/get_leave_request.py --employee-id <employee-id> --status PENDING --from-date <today> --to-date <end-of-next-year>`.
- Treat approval as a write action.
- **Mandatory User Confirmation & Turn Boundary**:
  - Before executing `approve_request.py`, **ALWAYS** present a preview of the request to approve:
    - **Request ID**: `<request_id>`
    - **Employee**: `<employee name>`
    - **Leave Type**: `<leave type name>`
    - **Dates**: `<start_date> to <end_date>`
  - Ask the user: *"Do you confirm approving this leave request?"*.
  - **STOP and wait for explicit user confirmation** (e.g. "yes", "confirm", "duyệt") in a subsequent turn before executing. **DO NOT execute the script in the same turn as presenting the preview.**
- Use the preferred execution command only after the exact `request_id` is known.

### Required arguments
- `request_id` — required leave request ID.

### Execution
- Preferred execution: `exec` with `python skills/timeoff/approve_request/scripts/approve_request.py --request-id <request-id>`.
