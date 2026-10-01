---
name: employee-helpdesk-get-hr-request
description: Read an Employee Helpdesk request workspace as an authorized HR manager, including form answers, current version, and available lifecycle actions.
side_effect: read
---

# Get HR Request

## Intent: employee-helpdesk-get-hr-request
### User request patterns
- open this HR request
- show HR request details ER-2026-000002
- review the employee request workspace
- which actions are allowed on this request now

### Retrieval tags
- employee-helpdesk
- hr-request
- request-detail
- read-action

### Answer objective
Retrieve the request detail (`request` with `version`, `status`, `assignee`, `queue`), `answers`, `form_schema`, and `available_actions` (each with `transition_key`, `target_status`, `requirements`).

### Instructions
- Requires the request UUID; resolve `ER-…` with `list_hr_requests --search` first. Never guess.
- Read this before any `manage_hr_request` call to obtain `request.version`; `available_actions` is empty until the request is assigned.
- Rely on backend authorization; a 403/404 means stop and report, not switch leaf.

### Required arguments
- `request_id`

### Execution
`python skills/employee_helpdesk/get_hr_request/scripts/get_hr_request.py --request-id <UUID>`
