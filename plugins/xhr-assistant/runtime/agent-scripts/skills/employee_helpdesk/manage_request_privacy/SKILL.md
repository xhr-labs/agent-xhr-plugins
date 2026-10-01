---
name: employee-helpdesk-manage-request-privacy
description: Execute or inspect backend-only privacy operations and legal holds on an Employee Helpdesk request for a manager holding the separate request-privacy permission.
side_effect: write
idempotency: key
read_actions: get_operation
---

# Manage Request Privacy (backend-only)

## Intent: employee-helpdesk-manage-request-privacy
### User request patterns
- place a legal hold on an HR request
- release the legal hold
- run a privacy operation for a request
- check privacy operation status

### Retrieval tags
- employee-helpdesk
- privacy
- legal-hold
- compliance
- write-action

### Answer objective
Run or inspect a request privacy operation through the backend privacy boundary, only for an explicitly authorized request.

### Instructions
- Privacy is a **separate permission** (`request_privacy` data block). HR inbox or case-handling access does not grant it, and neither does admin access to other modules. If unsure, explain this and stop; a 403 means stop.
- There is **no privacy screen in the Employee Helpdesk app**: these operations are backend-only. Never describe a menu, button, or path for them.
- Actions: `execute_operation` (body from an explicit, authorized instruction; do not invent operation types), `get_operation` (`--operation-id`), `place_hold`, `release_hold` (`--hold-id`). Writes need `--if-match <request version>`.
- Resolve exact request, operation, and hold UUIDs; preview the effect (data removed or frozen) without exposing protected content; STOP for explicit confirmation in a later turn.

### Execution
`python skills/employee_helpdesk/manage_request_privacy/scripts/manage_request_privacy.py --action <action> --request-id <UUID> [--if-match <version>] [--body-json '<json>']`
