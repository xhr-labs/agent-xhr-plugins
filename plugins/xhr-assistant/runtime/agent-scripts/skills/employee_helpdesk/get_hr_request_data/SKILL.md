---
name: employee-helpdesk-get-hr-request-data
description: Read HR request conversations, activities, attachments, transfer targets, view counts, or download links for an authorized HR manager.
side_effect: read
---

## Intent: employee-helpdesk-get-hr-request-data
### User request patterns
- show HR request messages
- show internal notes for this HR request
- show HR request activity
- list HR request attachments
- find transfer targets for this request
- show HR inbox counts
- download an HR attachment

### Retrieval tags
- employee-helpdesk
- hr-request
- messages
- activities
- attachments
- read-action

### Answer objective
Retrieve a specific HR workspace subresource without bypassing authorization.

### Instructions
- Supported `action` values are `view_counts`, `messages`, `internal_notes`, `activities`, `attachments`, `internal_attachments`, `transfer_targets`, `download_attachment`, and `download_internal_attachment`.
- Require exact request and attachment IDs where applicable.
- Internal notes and attachments remain HR-only; do not summarize them to an employee.

### Execution
`python skills/employee_helpdesk/get_hr_request_data/scripts/get_hr_request_data.py --action <action> [--request-id <UUID>] [--attachment-id <UUID>]`
