---
name: employee-management-dashboard
description: Propose and confirm People report filters, then fetch and present every Workforce Structure widget shown at /people?tab=reports, including six-month trends, structure breakdowns, movement tables and charts, offboarding, and employee type by department.
side_effect: read
---

# Employee Management Dashboard

## Intent: employee-management-dashboard
### User request patterns
- show the employee management dashboard
- show the People workforce reports
- check workforce structure for this month
- review headcount hiring and offboarding trends
- show employee type by department
- analyze workforce movement by organization

### Retrieval tags
- employee
- people
- workforce-report
- employee-management-dashboard
- headcount
- hiring
- offboarding

### Answer objective
Fetch the complete presentation model rendered by the People Reports tab at `/people?tab=reports`.

### Instructions
- Do not execute an initial dashboard request immediately. Propose the complete selection and ask the user to confirm or edit it.
- Default `month` to the current calendar month in the user's timezone.
- Default Department and Employee Type to All. Represent All by omitting the corresponding API argument.
- Show user-facing labels, never internal IDs, in the confirmation proposal.
- Execute only after explicit confirmation of the immediately preceding proposal. If any option changes, show the complete revised proposal and confirm again.
- On confirmation, execute immediately without asking a second time.
- The report always includes the selected month plus the preceding five months for timeline charts, matching the UI.
- Present the returned view model directly. Do not regroup, re-sort, or recalculate it unless the user asks for a different analysis.
- Empty arrays represent the UI empty state; do not infer that the company has no employees.
- If `sectionErrors` is non-empty, identify the affected widgets and present the remaining sections. Never replace unavailable values with zero.

### Default proposal
- Month: current calendar month.
- Department: All.
- Employee Type: All.

### UI section map
- `filterOptions`: Department and Employee Type options visible for the selected month.
- `timeline`: six-month total headcount plus new-hire/offboarding chart rows.
- `structure`: top-five active headcount by organization, employee type, work location, job title, and job-title type.
- `changeTables`: top-five department movement rows and employee-type movement rows with offboarding rate.
- `changeCharts`: top-eight job-title-type movement rows and monthly offboarding by department, including total offboarded.
- `employeeTypeByDepartment`: stacked active-headcount rows and series for up to eight visible departments.
- `sectionErrors`: widgets with unavailable or partially unavailable API data.

### Required arguments
- `month`: selected report month in `YYYY-MM` format.

### Optional arguments
- `departmentId`: selected Department ID; omit for All.
- `employeeTypeId`: selected Employee Type ID; omit for All.

### Execution
```text
python skills/employee/employee_management_dashboard/scripts/employee_management_dashboard.py --month <YYYY-MM> [--department-id <id>] [--employee-type-id <id>]
```
