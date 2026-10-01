---
name: employee-helpdesk-hr-inbox-help
description: Answer direct how-to questions about the HR Helpdesk inbox screen, assignment, SLA views, collaboration, and lifecycle buttons without calling tools.
---

# HR Inbox Help

## Intent: employee-helpdesk-hr-inbox-help
### User request patterns
- explain the HR Helpdesk inbox
- how does HR manage employee requests
- how do I assign an HR request in the app
- what are HR inbox filters and SLA views
- explain HR request collaboration

### Retrieval tags
- employee-helpdesk
- hr-inbox
- assignment
- sla
- direct-answer

### Answer objective
Explain how authorized HR managers work requests from intake to closure in the current app.

### Instructions
- Answer directly without calling executable tools.
- Refer to `manage_hr_request` when the user asks to perform an action; refer to `list_hr_requests` / `get_hr_request` for live data.
- Describe only controls that exist in the app (below). Do not mention a queue transfer button, a Queue Configuration screen, or a privacy screen: those are backend-only.

### Direct answer
The HR inbox lists requests with quick views (Inbox, My requests, Unassigned, Overdue, Completed), search, and filters for request type, status, assignment, priority, SLA risk, created date, and sort. Each row shows requester, status, assignee, due date; unassigned rows offer "Assign to me". The request detail workspace has a triage panel (change assignee with a reason, change priority with a reason, change due date with a reason in your timezone), lifecycle buttons generated from the backend's available actions (for example Resolve with a resolution code and summary, Request information which sends a public explanation and moves the case to Waiting for employee, Close after resolution), a Conversation tab (public replies and public files the employee can see) and an Internal tab (HR-only notes and files). SLA targets for first response and resolution come from the request type. Every action is checked by the service's tenant and ReBAC rules.
