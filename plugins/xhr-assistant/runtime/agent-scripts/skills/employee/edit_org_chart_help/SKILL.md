---
name: employee-edit-org-chart-help
description: Explain how authorized users edit reporting relationships from the People org chart. Use when the user asks how to change a line manager visually, add a direct report, assign a department manager, use chart depth or filters, or why edit mode is unavailable.
---

# Edit Org Chart Help

## Intent: employee-edit-org-chart-help
### User request patterns
- edit the organization chart
- change an employee line manager from the org chart
- add a direct report in the org chart
- assign a department line manager
- explain why org chart edit mode is unavailable

### Retrieval tags
- employee
- org-chart
- line-manager
- reporting-relationship
- direct-answer

### Answer objective
Explain permission-aware organization chart editing.

### Instructions
- Answer directly without calling executable tools.
- Use `fetch_org_chart` only when live organization data is requested.

### Direct answer
1. Open **People** and switch to **Org Chart**.
2. Use filters and the depth selector to load the relevant part of the organization.
3. If you have employee job-edit permission, enable edit mode.
4. Drag an employee onto a valid manager and confirm the reporting change, or open the employee's relationship actions to assign a manager, add a direct report, or set a department line manager.

Cards stay in the generated layout; dragging changes the reporting relationship, not the visual position. Users without the required permission can browse the chart but cannot enter edit mode.
