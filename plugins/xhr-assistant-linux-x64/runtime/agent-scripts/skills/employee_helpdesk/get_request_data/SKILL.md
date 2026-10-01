---
name: employee-helpdesk-get-request-data
description: Read messages, activities, attachments, or an attachment download link for an Employee Helpdesk request visible to the authenticated employee.
side_effect: read
---

## Intent: employee-helpdesk-get-request-data
### User request patterns
- show messages on my HR request
- show activity history for my request
- list attachments on my request
- download an attachment from my request

### Retrieval tags
- employee-helpdesk
- messages
- activities
- attachments
- read-action

### Answer objective
Retrieve one authorized request subresource.

### Instructions
- Supported `action` values are `messages`, `activities`, `attachments`, and `download_attachment`.
- Require exact request and attachment IDs where applicable.

### Execution
`python skills/employee_helpdesk/get_request_data/scripts/get_request_data.py --action <action> --request-id <UUID> [--attachment-id <UUID>]`
