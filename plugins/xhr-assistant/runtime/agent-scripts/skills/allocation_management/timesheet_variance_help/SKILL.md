---
name: allocation-management-timesheet-variance-help
description: Explain timesheet-versus-allocation variance in Allocation Management. Use when the user asks about planned allocation versus actual timesheets, allocation variance, or Workbench/Attendance comparison.
---

# Timesheet Variance Help

## Intent: allocation-management-timesheet-variance-help
### User request patterns
- compare timesheets with allocation
- explain allocation variance
- review planned versus actual work
- show timesheet variance by project
- compare allocation planning with attendance tracking
- explain why timesheet data is missing from a report
- explain positive or negative allocation variance

### Retrieval tags
- allocation-management
- timesheets
- variance
- attendance-tracking
- workbench
- unmapped-data
- direct-answer

### Answer objective
Explain how allocation plans can be compared with actual timesheet activity and how to diagnose incomplete comparisons.

### Instructions
- Answer directly without calling executable tools.
- Do not claim live variance numbers unless a reporting tool is explicitly used.
- Explain that variance is actual imported work minus planned allocation. Positive means actual work is higher than planned; negative means actual work is lower.
- Treat imported work as actual activity, not a replacement for allocation or capacity. Allocation remains the planning value.
- Explain that the comparison depends on a configured active integration, a selected date range, mapped project, mapped employee, and imported work items. Missing any one can reduce report totals.
- Explain that imported work can remain visible as unmapped while excluded from aggregate report totals until mapping is resolved and the affected period is refreshed.
- Use 8 hours as 1 man-day when explaining duration-based actual-work totals. Do not invent a local working-day schedule for timesheet conversion.
- When a user reports a mismatch, check platform activation, date range, sync status, project mapping, employee mapping, deleted source rows, and whether the report has refreshed after the correction.

### Direct answer
Open [Allocation Reports]({{allocation_reports_url}}) to review timesheet variance.

Timesheet variance compares planned allocation with actual work captured through a configured timesheet integration. It helps managers see whether a project is consuming more or less effort than planned.

When integrations are configured, Allocation Management can use project allocation data together with approved Attendance Tracking task activity or Workbench/YouTrack work items to show variance cards, comparison charts, or detail tables. If a project or employee is unmapped, inspect the Timesheet menu and fix the mapping before treating the report as complete.
