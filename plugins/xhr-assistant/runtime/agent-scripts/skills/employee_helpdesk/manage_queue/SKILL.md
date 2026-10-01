---
name: employee-helpdesk-manage-queue
description: Create, update, or retire an Employee Helpdesk queue for an authorized HR manager after confirmation.
side_effect: write
idempotency: key
---

## Intent: employee-helpdesk-manage-queue
### User request patterns
- create an HR request queue
- rename an Employee Helpdesk queue
- retire an HR queue

### Retrieval tags
- employee-helpdesk
- queues
- configuration
- write-action

### Answer objective
Apply one confirmed queue configuration action.

### Instructions
- Supported actions are `create`, `update`, and `retire`.
- Resolve the queue ID for update/retire; show the full payload and wait for explicit confirmation before execution.

### Execution
`python skills/employee_helpdesk/manage_queue/scripts/manage_queue.py --action <create|update|retire> [--queue-id <UUID>] [--body-json '<json>']`
