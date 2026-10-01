---
name: employee-helpdesk-list-hr-requests
description: Search the tenant-scoped Employee Helpdesk HR inbox for an authorized HR manager, including resolving ER ticket numbers to request UUIDs.
side_effect: read
---

# List HR Requests

## Intent: employee-helpdesk-list-hr-requests
### User request patterns
- show the HR request inbox
- search HR requests for employee <name>
- list overdue HR requests
- find unassigned Employee Helpdesk requests
- find request ER-2026-000002

### Retrieval tags
- employee-helpdesk
- hr-inbox
- search
- read-action

### Answer objective
Retrieve filtered HR inbox requests using service-supported filters, and resolve ticket numbers to UUIDs.

### Instructions
- To resolve `ER-YYYY-NNNNNN`, call with `--search <number>` and use the matching row's `id`.
- Summarize only returned rows; `count` is the page size, not the tenant total. Follow `meta.next_cursor` verbatim; when it is null say there is no next page.
- Do not bypass the service filters or infer access from an employee name. Opening a request is a read; never mutate from this leaf.

### Arguments
- Filters: `queue_id`, `request_type_id`, `assignee_id` (UUIDs), `status_key` (SUBMITTED | IN_PROGRESS | WAITING_FOR_EMPLOYEE | RESOLVED | CLOSED), `search`, `created_from`, `created_to` (ISO instants).
- Enums (exact values): `assignment` any | mine | unassigned · `sla_risk` normal | warning | breached · `view` inbox | mine | unassigned | overdue | completed · `priority` LOW | NORMAL | HIGH | URGENT · `sort` createdAt | updatedAt | resolutionDueAt | priority · `order` asc | desc.
- Paging: `cursor`, `page_size` (1-100).
- "At SLA risk" = `--sla-risk warning` (or `breached` when already overdue); "unassigned" = `--assignment unassigned` or `--view unassigned`.

### Execution
`python skills/employee_helpdesk/list_hr_requests/scripts/list_hr_requests.py [--search <text>] [--assignment unassigned] [--sla-risk warning] [--view overdue] [--status-key IN_PROGRESS] [--sort resolutionDueAt --order asc] [--cursor <cursor>] [--page-size <n>]`
