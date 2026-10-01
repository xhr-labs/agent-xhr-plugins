---
name: attendance-reports
description: Propose and confirm attendance report filters, then fetch and present Attendance Reports visible at /attendance/reports, including Approved and Waiting for approval tabs, month/week/annual view modes, hours against target, signed overtime and breakdowns, and annual balances.
side_effect: read
---

# Attendance Reports

## Intent: attendance-reports
### User request patterns
- show the attendance reports
- show timesheet reports for this month
- check waiting for approval timesheets report
- review approved attendance hours and overtime
- show annual attendance report for 2026
- check employee attendance report by department
- view attendance summary for an employee

### Retrieval tags
- attendance
- reports
- timesheet-reports
- attendance-reports
- timesheets
- overtime
- approved-hours
- waiting-for-approval
- annual-report

### Answer objective
Fetch the complete presentation model rendered by the Attendance Reports page at `/attendance/reports`.

### Instructions
- Do not execute an initial dashboard/report request immediately. Propose the complete selection and ask the user to confirm or edit it.
- Default `status` to `APPROVED`. When the user asks for pending or awaiting timesheets, use `PENDING`.
- Default `mode` to `month`.
- Default `month` to the current calendar month in the user's timezone (`YYYY-MM`).
- Default `departmentId` and `searchName` to All (omit from arguments).
- For `week` mode, accept or calculate inclusive `startDate` and `endDate` (`YYYY-MM-DD`).
- For `annual` mode, accept `year` (defaults to current year); annual reports represent approved attendance facts and 12-month balance progression.
- Show user-facing labels in the confirmation proposal.
- Execute only after explicit confirmation of the immediately preceding proposal. If any option changes, show the revised proposal and confirm again.
- On confirmation, execute immediately without asking a second time.
- Present the returned view model directly: KPI summary cards first, then the report rows table, and employee detail if requested.
- For `APPROVED` tab: Overtime Hours displays signed net balance minutes (`balanceMinutes`), and regular overtime is derived as total balance minus rest day and public holiday overtime.
- For `PENDING` tab (Waiting for approval): Overtime Hours displays recognized projected overtime.
- Empty arrays represent the UI empty state; do not infer that the company has no attendance records.

### Confirmation workflow
1. Build a proposed selection from the user's request and defaults below.
2. Show every selection in user-facing labels:
   - Status tab: `Approved` or `Waiting for approval`
   - Mode: `Month`, `Week`, or `Annual`
   - Month / Date range / Year
   - Department: `All` or selected department
   - Search Name: `All` or specified search keyword
3. Ask for confirmation before running.
4. Execute immediately on confirmation.

### Default proposal
- Status tab: `Approved`
- Mode: `Month`
- Month: Current calendar month (e.g. `2026-08`)
- Department: `All`
- Employee search: `All`

Example proposal:
```text
I will show the attendance reports with these options:
- Status: Approved
- Mode: Month
- Month: August 2026
- Department: All
- Employee: All

Confirm these options, or tell me what you want to change.
```

### UI section map
- `kpiSummary`: Overall summary metrics (total employees, approved/awaiting hours, target hours, signed overtime, regular/rest-day/holiday/night overtime).
- `reports`: Formatted report rows matching UI table (People, Approved / Awaiting Hours, Overtime Hours, Regular OT, Rest Day OT, Public Holiday OT, Target Hours, Department, Employment Type).
- `employeeDetail`: Detailed breakdown for a selected employee including progress bars, compliance violations, and daily timesheet entries.
- `sectionErrors`: Partial failures or error notifications if an API segment fails.

### Required arguments
- None (defaults to current month and APPROVED status).

### Optional arguments
- `status`: `APPROVED` or `PENDING` (defaults to `APPROVED`).
- `mode`: `month`, `week`, or `annual` (defaults to `month`).
- `month`: selected report month in `YYYY-MM` format (for `month` mode).
- `year`: selected report year in `YYYY` format (for `annual` mode).
- `startDate`, `endDate`: selected date range in `YYYY-MM-DD` format (for `week` mode).
- `departmentId`: selected Department ID; omit for All.
- `searchName`: employee name filter keyword.
- `employeeId`: drill-down employee ID for detailed entries.

### Execution
```text
python skills/attendance/attendance_reports/scripts/attendance_reports.py [--status <APPROVED|PENDING>] [--mode <month|week|annual>] [--month <YYYY-MM>] [--year <YYYY>] [--start-date <YYYY-MM-DD> --end-date <YYYY-MM-DD>] [--department-id <id>] [--search-name <name>] [--employee-id <id>]
```
