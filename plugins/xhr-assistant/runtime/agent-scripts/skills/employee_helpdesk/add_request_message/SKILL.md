---
name: employee-helpdesk-add-message
description: Add a public follow-up message to the authenticated employee's Employee Helpdesk request after confirmation.
side_effect: write
idempotency: key
---

# Add Employee Request Message

## Intent: employee-helpdesk-add-message
### User request patterns
- reply to my HR request
- add a message to request ER-2026-000001
- send this follow-up to HR
- provide the requested information on my request

### Retrieval tags
- employee-helpdesk
- message
- conversation
- write-action

### Answer objective
Append a public employee message to a request the caller owns.

### Instructions
- Resolve the request UUID with `list_my_requests` (match `request_number`), then `get_request` for the current `version` and status. Closed requests accept no messages: say so and stop.
- Show the message preview and wait for explicit confirmation in a later turn. A follow-up asking to check without resending means read only.
- Call once with `--if-match <version>` and a generated `--idempotency-key`. On `VERSION_CONFLICT`, refetch, show what changed, and ask again with the same key; never post twice.
- This is the employee leaf; never use `manage_hr_request add_public_message` for the caller's own request.

### Required arguments
- `request_id` (UUID), `body`, `if_match` (current version)

### Execution
`python skills/employee_helpdesk/add_request_message/scripts/add_request_message.py --request-id <UUID> --body "<message>" --if-match <version> --idempotency-key <uuid>`
