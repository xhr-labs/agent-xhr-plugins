---
name: get-pending-requests
description: List all time-off requests waiting for manager or admin approval.
side_effect: read
---

# Get Pending Requests (Approval Queue)

## Intent: get-pending-requests
### User request patterns
- show pending leave requests
- what time-off requests are waiting for approval?
- list approval queue

### Retrieval tags
- timeoff
- pending-requests
- approval-queue
- manager-approvals

### Instructions
- Run `get_pending_requests.py` to inspect all pending leave requests.
- Returns requester details, dates, leave type, and submitted notes.

### Optional arguments
- `page`: Page index (default `0`).
- `size`: Page size (default `50`).
- `department_id`: Filter by department UUID.
- `employee_name`: Filter by employee name.

### Execution
```text
python skills/timeoff/get_pending_requests/scripts/get_pending_requests.py [--department-id <UUID>] [--employee-name "<name>"]
```
