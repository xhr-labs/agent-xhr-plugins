---
name: reject-request
description: Reject a pending time-off request with a mandatory rejection note/reason after user confirmation.
side_effect: write
---

# Reject Time-Off Request

## Intent: reject-request
### User request patterns
- reject leave request
- decline time off request
- reject request with reason

### Retrieval tags
- timeoff
- reject-request
- decline-leave
- manager-rejection

### Instructions
- **Input Verification Rule**:
  - `request_id` is required and must be a valid UUID. If unknown, run `python skills/timeoff/get_pending_requests/scripts/get_pending_requests.py` to resolve `request_id`.
  - `reject_reason` should be provided to give clear feedback to the requester.
- **Mandatory User Confirmation & Turn Boundary**:
  - Before executing `reject_request.py`, **ALWAYS** present a preview:
    - **Request ID**: `<request_id>`
    - **Rejection Reason**: `<reason or "None">`
  - Ask the user: *"Do you confirm rejecting this leave request?"*.
  - **STOP and wait for explicit user confirmation** (e.g. "yes", "confirm", "từ chối") in a subsequent turn before executing. **DO NOT execute the script in the same turn as presenting the preview.**

### Required arguments
- `request_id`: UUID of the leave request to reject.

### Optional arguments
- `reject_reason`: Reason or note for the rejection.

### Execution
```text
python skills/timeoff/reject_request/scripts/reject_request.py --request-id <UUID> [--reject-reason "<reason>"]
```
