---
name: employee-helpdesk-list-queues
description: List tenant-scoped Employee Helpdesk HR queues for an authorized HR manager.
side_effect: read
---

## Intent: employee-helpdesk-list-queues
### User request patterns
- list HR request queues
- show Employee Helpdesk queues
- find the queue for payroll requests

### Retrieval tags
- employee-helpdesk
- queues
- read-action

### Answer objective
Retrieve configured HR queues with cursor pagination.

### Instructions
- Use this to resolve a queue ID before assignment, transfer, or request-type configuration.

### Execution
`python skills/employee_helpdesk/list_queues/scripts/list_queues.py [--cursor <cursor>] [--page-size <n>]`
