---
name: employee-helpdesk-get-request
description: Read one Employee Helpdesk request visible to the authenticated employee, including status, answers, and current version.
side_effect: read
---

# Get My Employee Request

## Intent: employee-helpdesk-get-request
### User request patterns
- show my request details
- open Employee Helpdesk request ER-2026-000001
- check the status of my request
- what does HR need from me on this request

### Retrieval tags
- employee-helpdesk
- request-detail
- read-action

### Answer objective
Retrieve a tenant-scoped request detail by UUID.

### Instructions
- Requires the request UUID. A ticket number (`ER-…`) must first be resolved with `list_my_requests` (field `id`); do not guess, and do not use the caller's employee ID.
- Do not broaden to HR leaves when the request is not found or not permitted; report the backend answer.
- Use `get_request_data --action messages` for the conversation (HR explanations) and `activities` for history.

### Required arguments
- `request_id`

### Execution
`python skills/employee_helpdesk/get_request/scripts/get_request.py --request-id <UUID>`
