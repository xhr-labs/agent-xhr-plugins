---
name: employee-helpdesk-list-eligible-assignees
description: Find eligible HR assignees for a tenant-scoped Employee Helpdesk queue.
side_effect: read
---

# List Eligible HR Assignees

## Intent: employee-helpdesk-list-eligible-assignees
### User request patterns
- find HR assignees for queue <id>
- search eligible HR managers
- who can I assign this request to

### Retrieval tags
- employee-helpdesk
- assignees
- assignment
- read-action

### Answer objective
Return only the bounded assignee directory authorized for the queue.

### Instructions
- Use this read-only tool before assignment or transfer when the assignee ID is unknown.
- Do not fall back to an unfiltered employee directory.

### Required arguments
- `queue_id`

### Optional arguments
- `search`
- `cursor`
- `page_size`

### Execution
`python skills/employee_helpdesk/list_eligible_assignees/scripts/list_eligible_assignees.py --queue-id <UUID> [--search <text>]`
