---
name: allocation-management-troubleshooting-help
description: Diagnose Allocation Management setup, permission, eligibility, calculation, project, report, period-lock, and integration problems. Use for complex symptoms and edge cases.
---

# Allocation Management Troubleshooting Help

## Intent: allocation-management-troubleshooting-help
### User request patterns
- troubleshoot Allocation Management setup
- explain why an employee cannot be allocated
- explain why an employee is missing from Allocation
- diagnose an allocation save error
- diagnose a locked allocation month
- explain unexpected capacity or utilization
- troubleshoot missing dashboard or report data
- troubleshoot unmapped timesheets
- fix a failed Allocation synchronization
- check whether permissions cause an Allocation error

### Retrieval tags
- allocation-management
- troubleshooting
- edge-cases
- permissions
- employee-eligibility
- FTE
- CAP
- PROD
- capacity
- project-status
- overlap
- period-lock
- reports
- integrations
- timesheets

### Answer objective
Guide the user through the smallest safe checks for Allocation Management failures and explain when an Admin, HR user, project owner, or integration administrator must intervene.

### Direct answer
Start from [Allocation Management]({{allocation_url}}).

### Instructions
- Answer in user-facing terms. Do not expose service names, database tables, raw API paths, request payloads, bearer tokens, or implementation stack details.
- Identify the symptom first, then give checks in order. Do not ask the user to repeat a check that already passed.
- Separate permission failures from data failures. An Admin may have broad access only when Allocation Management is installed and the app permission is present; a normal employee or project manager may have intentionally narrower access.
- For an employee missing from the allocation picker, check active status, production eligibility, resolved FTE greater than zero, and whether Allocation data has refreshed. Do not assume CAP alone controls picker visibility.
- For an employee rejected during save, check resolved FTE, CAP enabled, allocation write access for the employee or project owner department, and the selected project's access/state.
- For FTE problems, check the employee Job Details FTE first, then Employee Type FTE. A blank, invalid, or zero result leaves no usable FTE. Do not tell users to set an employee override when the employee type default is correct.
- For capacity or utilization differences, check work location, working days, public holidays, approved unpaid leave, approved maternity leave, date range, and allocation percentage. Holidays are removed before leave reductions, and a half-day leave reduces capacity by half a working day.
- For a project allocation failure, check that the project is active/open for new allocation, the date range is valid, the employee/project dates do not overlap an existing row for the same project, and every month touched by the date range is open.
- For a locked-month error, explain that create, edit, and delete are all blocked for any allocation touching the locked month. Recommend unlocking only through the company's period-control process; do not suggest bypasses.
- For an unexpected warning, explain that over-allocation compares total planned effort with available capacity for the month. A warning is not automatically a save failure.
- For missing report rows or totals, check report permissions, timeline and filters, employee/department SOURCE values, project owner department, status filter, stale employee data, and whether the relevant source data has been imported and mapped.
- For Source Line and Allocated Line mismatches, explain that Source Line comes from the employee's department and Allocated Line comes from the project's owner department. Check both records and refresh Allocation data after correcting profile values.
- For timesheet variance gaps, check active integration, sync result, date range, project mapping, employee mapping, deleted source work, and report refresh. Unmapped imported rows may be visible but excluded from aggregate comparisons.
- For partial or failed synchronization, fix the connection or mapping issue, review the run summary, and retry only when no sync is currently running. Never claim success without a reported successful result.
- If the symptom remains after these checks, collect the company, affected employee/project, month, exact visible message, and recent setup change. Do not request credentials or tokens.

### Diagnostic matrix

| Symptom | Most likely checks | Safe next action |
| --- | --- | --- |
| Employee missing from picker | Active status, PROD, FTE, refresh | Correct profile values and refresh Allocation data |
| FTE greater than zero error | Job Details FTE, then Employee Type FTE | Set one valid positive FTE and refresh |
| Employee excluded from capacity | CAP value | Enable capacity tracking when appropriate; recalculate the plan |
| Permission denied | App installed, user's Allocation permission, employee/project department scope | Ask an Admin to review Allocation permissions |
| Project cannot receive row | Project status, dates, project access, duplicate overlap | Use an open project and a non-overlapping range |
| Month locked | Any touched month is locked | Follow the period owner process to unlock, then retry |
| Capacity looks wrong | Work location calendar, holidays, approved leave, date range | Correct calendar/leave data and recalculate |
| Source Line is blank | Department SOURCE value or stale profile data | Set a consistent department value and refresh |
| Dashboard/report is empty | Permission, filters, no allocations, no imported actuals | Clear filters and confirm source data exists |
| Timesheet row is unmapped | Project or employee mapping | Fix mapping, rerun or retry sync, then refresh report |
| Sync is partial/failed | Connection, selected projects, date range, unmapped counts | Fix the cause and retry after the current run ends |

### Escalation boundary

- Ask an Admin to install the app, manage App Permissions, create the five custom fields, refresh Allocation data, unlock a period, or configure integrations.
- Ask HR to correct employee type, job, department, work location, leave, and custom-field values.
- Ask the project owner or project access administrator to correct project ownership, project status, project dates, or project access.
- Escalate to product support only after the visible message, affected records, month, permissions, setup values, and sync status have been checked. Never include access tokens in the escalation.
