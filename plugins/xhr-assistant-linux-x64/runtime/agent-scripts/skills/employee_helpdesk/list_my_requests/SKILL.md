---
name: employee-helpdesk-list-my-requests
description: List the authenticated employee's Employee Helpdesk requests with cursor pagination.
side_effect: read
---

# List My Employee Requests

## Intent: employee-helpdesk-list-my-requests
### User request patterns
- show my HR requests
- list my employee requests
- find my open requests
- check my request history

### Retrieval tags
- employee-helpdesk
- my-requests
- list
- read-action

### Answer objective
Return only requests visible to the authenticated employee.

### Instructions
- The service scopes results to the authenticated employee and tenant.
- Use the returned cursor for subsequent pages.

### Arguments
- `cursor` (optional)
- `page_size` (optional)

### Execution
`python skills/employee_helpdesk/list_my_requests/scripts/list_my_requests.py [--cursor <cursor>] [--page-size <n>]`
