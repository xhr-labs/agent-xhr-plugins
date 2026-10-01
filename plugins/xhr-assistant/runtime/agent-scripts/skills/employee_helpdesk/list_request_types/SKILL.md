---
name: employee-helpdesk-list-configured-types
description: List configured Employee Helpdesk request types and versions for an authorized HR manager.
side_effect: read
---

## Intent: employee-helpdesk-list-configured-types
### User request patterns
- list configured Employee Helpdesk request types
- show request type versions
- find a draft request type

### Retrieval tags
- employee-helpdesk
- request-types
- configuration
- read-action

### Answer objective
Retrieve the HR request catalog configuration.

### Instructions
- Use the returned IDs and versions to drive request-type configuration actions.
- Do not treat a draft as employee-submittable until it is published.

### Execution
`python skills/employee_helpdesk/list_request_types/scripts/list_request_types.py [--cursor <cursor>] [--page-size <n>]`
