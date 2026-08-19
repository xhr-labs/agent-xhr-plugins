---
name: allocation-management-dashboard
description: Propose and confirm dashboard timeline and filters, then fetch and present Allocation Management metric cards and Summary, Utilization, Allocation by Line, and Timesheet sections.
side_effect: read
---

# Allocation Management dashboard

## Intent: allocation-management-dashboard
### User request patterns
- show the allocation management dashboard
- show resource allocation for this month
- review utilization and capacity for a reporting period
- show allocation by project status and project type
- show own-line and cross-line allocations
- compare planned allocation with actual timesheets
- find underutilized or overutilized employees

### Retrieval tags
- allocation-management
- dashboard
- resource-allocation
- utilization
- allocation-by-line
- timesheet-variance
- confirmation-required

### Answer objective
Fetch the complete dashboard dataset and present the same business sections visible in the Allocation Management UI.

### Instructions
- Do not execute immediately from an initial dashboard request. First propose a complete dashboard selection and ask the user to confirm or edit it.
- Use the current calendar month in the user's timezone as the default `month` when the user does not specify a reporting period.
- `timeline` defaults to `MONTH` and accepts `MONTH`, `QUARTER`, `YTD`, or `RANGE`.
- In `MONTH`, KPI cards and breakdown charts use the selected month, while utilization trends, monthly utilization tables, and Timesheet use the selected month plus the two preceding months, matching the UI.
- In `QUARTER`, use the quarter start through the selected month.
- In `YTD`, use January through the selected month.
- In `RANGE`, require `fromMonth` and `toMonth`; the KPI cards use `toMonth` while charts and trends use the inclusive range.
- Default every visible resource filter to `All`: Source Line, Allocated Line, Department, Project, and Employee Type. Represent `All` by omitting the corresponding API argument.
- Pass a filter argument only when the user selected or confirmed a specific value.
- The output is grouped under `sections.metricCards`, `sections.summary`, `sections.utilization`, `sections.allocationByLine`, and `sections.timesheet`.
- Present only sections relevant to the user's question. For a general dashboard request, show metric cards first, then concise highlights from every section.
- Treat man-month values as `MM` and utilization values as percentages.
- For timesheet variance, positive means actual timesheet MM is above allocated MM; negative means it is below allocated MM.
- Do not invent missing values. Empty arrays represent the UI empty state.
- The backend APIs accept one value per filter. If the user selects several values for the same filter, execute once for each filter combination and combine the results without double-counting.

### Confirmation workflow
1. Build a proposed selection from the user's request and the defaults below.
2. Show every selection in user-facing labels, not internal IDs:
   - Timeline
   - Selected month, or From month and To month for `RANGE`
   - Source Line
   - Allocated Line
   - Department
   - Project
   - Employee Type
3. Ask for explicit confirmation before execution, even though this is a read-only report.
4. Do not call the runtime entrypoint until the user replies with a clear approval such as `confirm`, `yes`, `continue`, `show it`, or an equivalent affirmative response to the immediately preceding proposal.
5. If the user changes any option, show the revised complete selection and ask for confirmation again.
6. On the confirmation turn, execute immediately with the confirmed values. Do not ask for a second confirmation.
7. A general request such as `show dashboard`, `view allocation`, or `check utilization` is intent to prepare the report, not confirmation of the proposed defaults.

### Default proposal
- Timeline: `MONTH` (According to month).
- Selected month: current calendar month in the user's timezone.
- Source Line: All.
- Allocated Line: All.
- Department: All.
- Project: All.
- Employee Type: All.
- For `RANGE`, if the user chooses the timeline without dates, initially propose the current month for both From month and To month, matching the UI, then require confirmation.

Example proposal:
```text
I will show the dashboard with these options:
- Timeline: According to month
- Month: August 2026
- Source Line: All
- Allocated Line: All
- Department: All
- Project: All
- Employee Type: All

Confirm these options, or tell me what you want to change.
```

### UI section map
- `metricCards`: allocated projects, total allocated MM, internal resources, and borrowed resources.
- `summary`: the six UI chart datasets: allocation by project type, allocation by project status, employee count by project status, allocation by project, utilization trend, and utilization by department. Bar charts are already filtered, sorted, grouped, and limited like the UI.
- `utilization`: employee detail with utilization and timesheet variance; department-by-month rows; employee-by-month rows; monthly totals; and the overall total.
- `allocationByLine`: project-status table with total, employee-status table with total, source-line by allocated-line MM matrix with row/column/grand totals, project source-vs-own rows with total, and employee allocation rows.
- `timesheet`: allocation-vs-timesheet monthly trend, comparison by line, comparison by project, project detail with MM/% variance, and project-by-month matrix with row/month/grand totals.
- Treat these output objects as the dashboard presentation model. Do not regroup or recalculate them unless the user asks for a different analysis.

### Required arguments
- `month`: selected dashboard month in `YYYY-MM` format.

### Optional arguments
- `timeline`: `MONTH`, `QUARTER`, `YTD`, or `RANGE`; defaults to `MONTH`.
- `fromMonth`, `toMonth`: inclusive reporting range, required only for `RANGE`.
- `departmentId`, `employeeTypeId`, `workLocationId`, `jobTitleId`
- `sourceLineKey`, `allocatedLineKey`, `productLineId`, `projectId`, `employeeId`

### Execution
```text
python skills/allocation_management/dashboard/scripts/dashboard.py --month <YYYY-MM> [--timeline <MONTH|QUARTER|YTD|RANGE>] [--from-month <YYYY-MM> --to-month <YYYY-MM>] [filters]
```
