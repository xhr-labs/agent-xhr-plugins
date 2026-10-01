---
name: employee-helpdesk-permissions-help
description: Answer direct questions about Employee Helpdesk employee and HR manager permissions, ReBAC, and tenant-scoped visibility without calling tools.
---

# Employee Helpdesk Permissions Help

## Intent: employee-helpdesk-permissions-help
### User request patterns
- explain Employee Helpdesk permissions
- who can see HR requests
- can an employee see another employee's request
- what can an HR manager do in Employee Helpdesk
- explain Employee Helpdesk ReBAC

### Retrieval tags
- employee-helpdesk
- permissions
- rebac
- hr-manager
- direct-answer

### Answer objective
Explain permission boundaries without exposing authorization internals as a workaround.

### Instructions
- Answer directly without calling executable tools.
- Never suggest bypassing ReBAC, tenant checks, or the app permission manifest.

### Direct answer
Employees can submit and view their own requests and use the public conversation allowed by the request lifecycle. Authorized HR managers can work tenant requests, including inbox, assignment, lifecycle, collaboration, request-type configuration, reports, and privacy operations according to their granted data-block permissions. The backend checks both ReBAC decisions and local tenant/request ownership rules; an unavailable authorization service fails closed.
