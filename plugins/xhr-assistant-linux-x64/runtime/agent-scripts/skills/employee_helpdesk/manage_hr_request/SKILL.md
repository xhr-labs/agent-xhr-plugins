---
name: employee-helpdesk-manage-hr-request
description: Perform authorized HR-manager actions on an Employee Helpdesk request - assign, change priority or due date, lifecycle transitions (resolve, close, wait for employee), public replies, internal notes, and attachment intents.
side_effect: write
idempotency: key
---

# Manage HR Request

## Intent: employee-helpdesk-manage-hr-request
### User request patterns
- assign this HR request to <name>
- move the request to waiting for employee
- resolve or close this HR request
- change request priority or due date
- reply to the employee as HR
- add an internal HR note

### Retrieval tags
- employee-helpdesk
- hr-request
- assignment
- lifecycle
- resolve
- internal-note
- write-action

### Answer objective
Execute one explicit, confirmed HR request operation with the current request version.

### Instructions
- Resolve the request UUID first: `list_hr_requests --search ER-2026-000002` → field `id`. Then `get_hr_request --request-id <UUID>` for `request.version`, `request.queue.id`, `request.assignee`, and `available_actions`.
- Every action needs `--if-match <version>`: the `version` from the latest `get_hr_request`, or the `version` returned by the previous write in the same flow. Missing or stale version → the script/backend rejects; refetch and re-preview, never replay blindly.
- Assignee UUIDs come from `list_eligible_assignees --queue-id <request.queue.id> --search <name>`; never guess an employee UUID.
- Present a preview (action, target request number, payload, who can see the result) and STOP for explicit confirmation in a later turn. A request to preview, only check, or not execute yet means no call in that turn.
- One backend validation error → report and ask; do not retry with altered payloads.

### Actions and body (`--body-json`)
| action | body keys (required / optional) | notes |
|---|---|---|
| `assign` | `assignee_id` / `reason` | `reason` is required when assigning someone other than yourself |
| `change_priority` | `priority`, `reason` | priority ∈ LOW, NORMAL, HIGH, URGENT |
| `override_due_date` | `resolution_due_at`, `reason` | ISO-8601 instant in the future (convert the user's date and time from the profile timezone); no change without a reason |
| `transition` | `transition_key` / `reason`, `resolution_code`, `resolution_summary` | `transition_key` only from `available_actions[].transition_key` (e.g. `IN_PROGRESS_TO_RESOLVED`, `IN_PROGRESS_TO_WAITING_FOR_EMPLOYEE`, `RESOLVED_TO_CLOSED`); include every key listed in that action's `requirements` |
| `add_public_message` | `body` / `client_message_id` | employee can see it |
| `add_internal_note` | `body` / `client_note_id` | HR only; never a substitute for a required public explanation |
| `transfer` | `queue_id` / `assignee_id`, `reason` | backend-only; the app has no transfer button |
| `initialize_public_attachment` / `initialize_internal_attachment` | `display_name`, `mime_type`, `byte_size` | creates an upload intent only; bytes cannot be sent from chat → hand off to the app uploader |
| `complete_*_attachment` | none (`--intent-id`) | only after the file was actually transferred |
| `claim_*_attachment` | `intent_id` | attaches a completed intent |

### Flows
- **Wait for employee**: `available_actions` shows `requirements.public_explanation=true` → first `add_public_message` (the explanation), then `transition` with `--if-match` set to the `version` returned by that message. If the message succeeds and the transition fails, say so; do not repost the message.
- **Resolve → close**: `transition` to RESOLVED with `resolution_code` and `resolution_summary` (both required by that action), then refetch `available_actions` and ask again before `RESOLVED_TO_CLOSED`. Each step is its own confirmation.
- `available_actions` is empty for SUBMITTED requests that have no assignee; assign first.

### Required arguments
- `action`, `request_id` (UUID), `if_match` (current version)

### Optional arguments
- `intent_id`, `body_json`, `idempotency_key`

### Execution
`python skills/employee_helpdesk/manage_hr_request/scripts/manage_hr_request.py --action <action> --request-id <UUID> --if-match <version> [--body-json '<json>'] [--intent-id <UUID>]`
