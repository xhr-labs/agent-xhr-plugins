---
name: timeoff-cancel-request
description: Cancel one or more leave requests after the request IDs are known and confirmed. Use when the user asks to cancel, withdraw, or revoke an existing leave request.
---

# Cancel Leave Request

Use this leaf only after the target leave request IDs are known and confirmed.

# Intent Map

## Intent: cancel-confirmed-leave-requests
### User request patterns
- cancel this leave request
- cancel my leave request
- cancel my leave for next week
- withdraw this leave request
- cancel these leave requests
- cancel leave request

### Retrieval tags
- timeoff
- cancel
- leave-request
- write-action

### Answer objective
Cancel the confirmed leave request IDs and clearly report which requests were targeted.

### Instructions
- Require confirmed `request_ids` before execution.
- First decide whether the target leave request belongs to the current employee or another employee.
- If the user's wording is personal, such as `my leave request`, `my leave`, `my pending leave`, or another clearly self-referential phrasing, treat the lookup scope as the current employee and use `--mine true` in the helper leave-request lookup.
- If the user is asking about another employee, first resolve that employee by running `python skills/employee/search_employees/scripts/search_employees.py --name "<required name or keyword>"` and keep the resolved `employee_id` visible for the helper leave-request lookup.
- If `request_ids` are missing, first use `get_leave_request` to find candidate pending requests and keep the returned IDs visible.
- If the user already provided a date or date range, include it in that helper command using `--from-date YYYY-MM-DD --to-date YYYY-MM-DD`.
- If the user did not provide a date or date range, default the helper lookup window to `from_date=today` and `to_date=end of next year`.
- Example helper command for the current employee when dates are known: `python skills/timeoff/get_leave_request/scripts/get_leave_request.py --mine true --status PENDING --from-date YYYY-MM-DD --to-date YYYY-MM-DD`.
- Example helper command for the current employee when dates are not given: `python skills/timeoff/get_leave_request/scripts/get_leave_request.py --mine true --status PENDING --from-date <today> --to-date <end-of-next-year>`.
- Example helper command for another employee when dates are known: `python skills/timeoff/get_leave_request/scripts/get_leave_request.py --employee-id <employee-id> --status PENDING --from-date YYYY-MM-DD --to-date YYYY-MM-DD`.
- Example helper command for another employee when dates are not given: `python skills/timeoff/get_leave_request/scripts/get_leave_request.py --employee-id <employee-id> --status PENDING --from-date <today> --to-date <end-of-next-year>`.
- If the helper returns multiple possible requests, ask the user which exact request or requests to cancel, or ask for explicit confirmation of the exact IDs, before continuing.
- Treat cancellation as a write action.
- **Mandatory User Confirmation & Turn Boundary**:
  - Before executing `cancel_request.py`, **ALWAYS** present a preview of the request(s) to cancel:
    - **Target Request(s)**: `<request_ids>`
    - **Leave Type & Dates**: `<leave details>`
  - Ask the user: *"Do you confirm cancelling this leave request?"*.
  - **STOP and wait for explicit user confirmation** (e.g. "yes", "confirm", "hủy") in a subsequent turn before executing. **DO NOT execute the script in the same turn as presenting the preview.**
- Pass repeated `--request-ids` flags such as `--request-ids req-1 --request-ids req-2`.

### Required arguments
- `request_ids` — required list of leave request IDs to cancel.

### Execution
- Preferred execution: `exec` with `python skills/timeoff/cancel_request/scripts/cancel_request.py --request-ids req-1 --request-ids req-2`.
