---
name: approve-all-pending-requests
description: Bulk approve all pending time-off requests in the approval queue after explicit user confirmation.
side_effect: write
---

# Approve All Pending Requests

## Intent: approve-all-pending-requests
### User request patterns
- approve all pending leave requests
- bulk approve time off requests

### Retrieval tags
- timeoff
- bulk-approve
- approve-all
- approval-queue

### Instructions
- **Input Verification Rule**:
  - Run `python skills/timeoff/get_pending_requests/scripts/get_pending_requests.py` first to inspect how many requests will be approved.
- **Mandatory User Confirmation & Turn Boundary**:
  - **ALWAYS** display the count and summary of pending requests to be approved.
  - Ask the user: *"Do you confirm bulk-approving all [N] pending leave requests?"*.
  - **STOP and wait for explicit user confirmation** in a subsequent turn before executing. **DO NOT execute the script in the same turn as presenting the preview.**

### Execution
```text
python skills/timeoff/approve_all_pending_requests/scripts/approve_all_pending_requests.py
```
