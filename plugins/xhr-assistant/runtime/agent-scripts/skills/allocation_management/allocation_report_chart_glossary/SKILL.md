---
name: allocation-management-report-chart-glossary
description: Explain every visible Allocation Management report chart and metric, including utilization, internal and borrowed resources, allocation distributions, line views, project trends, and timesheet variance.
---

# Allocation Management Report Chart Glossary

## Intent: allocation-management-report-chart-glossary
### User request patterns
- explain how utilization is calculated
- explain what internal resources means
- explain what borrowed resources means
- explain an Allocation dashboard chart
- explain a project report chart
- explain allocation by project type
- explain allocation by project status
- explain the utilization trend
- explain own-line and cross-line allocation
- explain allocation versus timesheet variance
- explain why a report chart is empty
- explain why report percentages look different
- explain how allocation percentage is calculated
- explain MM or man-months
- explain MD or man-days

### Retrieval tags
- allocation-management
- allocation-reports
- chart-glossary
- dashboard
- utilization
- capacity
- internal-resources
- borrowed-resources
- own-line
- cross-line
- man-months
- timesheet-variance
- project-reports
- allocation-table
- man-days

### Answer objective
Give a precise, user-friendly explanation of every visible Allocation Management report chart and metric, including what is counted, the time range, the filters, and the common reasons a value may be zero or missing.

### Instructions
- Answer chart-definition questions directly. Do not call the dashboard fetch tool unless the user also asks for live report values.
- Use the chart's visible title and explain the unit first: employee count, FTE, MM, MD, or percentage.
- Use `MM` for man-months and `MD` for man-days. Explain them in plain language when the user may not know the terms.
- Explain `% allocation` as the planning input on an Allocation row, not as a calculated utilization percentage. It is the share of standard working days assigned to a project.
- Explain `MD` as available working days in the allocation date range multiplied by the allocation percentage. Explain `MM` as the resulting man-days normalized against the month's working days; calculate each month separately for a multi-month row and then add the results.
- Explain that FTE affects capacity and utilization comparisons, but does not multiply the allocation row's MD/MM value. A part-time employee can therefore be over capacity at a lower or equal allocation percentage.
- Explain utilization as `total allocated MM / total capacity MM * 100`. Calculate the ratio from the totals for the selected scope; do not average department or employee percentages.
- When presenting the formula in display math, escape the percent sign so it renders correctly: `$$\text{Utilization (\%)} = \frac{\text{Total allocated MM}}{\text{Total capacity MM}} \times 100$$`. Never place a raw `%` inside the math expression.
- Explain capacity as the available working capacity of active, production-enabled, capacity-counted employees with a valid positive FTE. Available days reflect work-location working days, public holidays, and approved unpaid or maternity leave.
- If capacity is zero, explain that utilization is displayed as 0% rather than dividing by zero. Do not interpret 0% as proof that no allocation exists without checking allocated MM.
- Explain Internal resources as own-line assignments: the employee's department Source Line matches the project owner's Allocated Line. Explain Borrowed resources as cross-line assignments: they do not match.
- Explain that internal/borrowed resource totals are based on employee-project-month allocation assignments in the selected scope. An employee assigned to several projects can appear more than once; do not automatically describe the count as unique people.
- Explain Source Line as the employee's department line and Allocated Line as the project owner's department line. Missing values are shown as unassigned/unknown and can affect line charts.
- Explain that a dashboard Month view uses the selected month for KPI and breakdown charts. Its utilization trend and monthly tables include the selected month and the two preceding months. Quarter, YTD, and Range use their selected inclusive periods.
- Explain that the dashboard Summary charts use allocated MM unless the title says employee count or utilization percentage.
- Explain that planning-status charts use Planned, Unverified, and Tentative allocations. These are planning labels, not project lifecycle statuses.
- Note the current dashboard label nuance: the charts titled Allocation by project statuses and Allocated employee count by project status are currently built from allocation planning status data, so explain them using Planned, Unverified, and Tentative unless the UI/source is changed.
- Explain project lifecycle statuses such as Planning, Ongoing, or Closed only for a chart or report that explicitly uses project lifecycle status data.
- Explain that charts are filtered by the selected report filters. Clearing a filter means all values; an empty result means no data matched the current scope, not necessarily that the company has no data.
- Explain that visible bar charts are sorted by value and may show only the largest visible categories. Do not infer that an omitted small category does not exist.
- Explain timesheet variance as actual imported work minus allocated work. Positive variance means actual work is higher; negative variance means actual work is lower. If allocated work is zero, percentage variance is not meaningful and is shown as zero or unavailable depending on the view.
- Explain that imported timesheet data must have an active integration, a mapped employee, a mapped project, and a matching date range to contribute to aggregate reports.
- Do not expose database names, endpoint paths, DTO names, query implementation, or internal service details.
- Do not invent definitions for hidden, deprecated, or unavailable report screens. If the user names a chart not listed below, say that its current visibility needs verification.

### Core metric definitions

| Metric | Meaning | How to interpret it |
| --- | --- | --- |
| Total employees | Working employee headcount for the selected month | It can differ from total active headcount because maternity and long-term unpaid leave are excluded from working employees. |
| Total FTE | Sum of valid FTE for the report scope | It represents workforce size in full-time equivalents, not a headcount. |
| Capacity MM | Available employee capacity expressed in man-months | It is reduced by non-working days, public holidays, and eligible approved leave. |
| Allocated MM | Planned allocation effort in man-months | It includes the allocation rows in the selected scope and status filter. |
| Resource utilization | Allocated MM divided by capacity MM | Over 100% means planned effort exceeds available capacity. |
| Internal resources | Own-line employee-project-month assignments | The employee and project owner belong to the same Source Line. |
| Borrowed resources | Cross-line employee-project-month assignments | The employee and project owner belong to different lines. |
| Timesheet variance | Actual imported work minus allocated work | Positive is above plan; negative is below plan. |

### Dashboard Summary charts

| Chart | What it shows | Unit and interpretation |
| --- | --- | --- |
| Allocation by project type | Allocated effort grouped by project type | MM. Larger bars represent more planned effort in that project type. |
| Allocation by project statuses | Allocated effort grouped by allocation planning status in the current dashboard implementation | MM. Explain the bars as Planned, Unverified, and Tentative; do not describe them as Planning, Ongoing, or Closed project totals. |
| Allocated employee count by project status | Allocation assignments grouped by Planned, Unverified, or Tentative status in the current dashboard implementation | Employee/assignment count. It is about planning confidence/status, not whether the project is open or closed. |
| Allocation by project | Allocated effort grouped by project | MM. Projects are ranked by allocated effort; smaller projects may be omitted when the chart limit is reached. |
| Utilization trending | Overall utilization across the trend months | Percentage. Read the line month by month; compare the percentage with capacity and allocated MM before concluding that staffing changed. |
| Utilization by department | Utilization calculated separately for each department | Percentage. A department with zero capacity is shown as 0%; compare its allocated and capacity MM as well. |

### Utilization tab

- **Employee utilization detail** shows each employee's allocated MM, capacity MM, utilization, actual timesheet MM when available, variance, and own-line/cross-line planning percentages. A high percentage means the employee's plan consumes most or more than all available capacity.
- **Utilization by department x month** shows one department across the selected months. The total percentage is calculated from the department's summed allocated MM and summed capacity MM for the displayed period.
- **Utilization by employee x month** shows one employee across the selected months. If an employee has several allocation rows, their monthly allocations are combined before utilization is calculated.
- **TS (MM)** is imported actual work converted to man-months. It is not part of the allocation numerator; it is a comparison value.
- **+/- MM** is actual timesheet MM minus allocated MM. **+/- %** uses allocated MM as the denominator when allocated MM is non-zero.

### Allocation by Line tab

- **Allocation by project line and planning status** groups allocated MM by the project's Allocated Line and Planned, Unverified, or Tentative status.
- **Allocation by employee line and planning status** groups allocated MM by the employee's Source Line and planning status.
- **Source Line x Allocated Line matrix** compares where employees belong with where their planned effort is used. Diagonal cells represent own-line work; off-diagonal cells represent cross-line or borrowed work.
- **Allocation by project - Source-line / Own-line** shows each project split between borrowed effort and own-line effort. The project total is the sum of both known categories; unknown line values may be excluded from this split.
- **Employee allocation tables** show the employee's allocation by line and planning status. Percentages use that employee's capacity as the denominator when capacity is available.

### Timesheet tab

- **Allocation vs Timesheet trend by month** compares allocated MM with imported timesheet MM for each month.
- **Allocation and Timesheet by project line** compares planned and actual MM grouped by Allocated Line.
- **Allocation and Timesheet by project** compares planned and actual MM for each project. Positive differences indicate more actual work than planned.
- **Project detail variance** shows allocated MM, actual timesheet MM, difference in MM, and difference percentage. A variance threshold may display only projects whose absolute variance is greater than 10%.
- **Project x month matrix** shows the same planned and actual comparison by project and month, making timing shifts visible even when the period total looks balanced.

### Project Details Reports tab

- **Total Allocation** shows total MD, MM, employee count, and allocation-slice count for the selected project and timeline.
- **TS / Alloc variance** compares the project's imported actual work with its allocation. Positive means actual work is above plan; negative means actual work is below plan.
- **Allocation vs Timesheet** compares the project's total allocated MM and actual timesheet MM for the selected timeline and planning-status filter.
- **Allocation & Timesheet detail** compares allocation and actuals per employee. Rows can include an employee with allocation only, timesheet only, or both.
- **Allocation by role** groups project allocation by project role in MM.
- **Allocation by employee** groups project allocation by employee in MM.
- **Employees by planning status** counts project assignment rows for Planned, Unverified, and Tentative allocations.
- **Own line / Source line split** compares effort from the project owner's line with effort from other lines. Explain Source-line as borrowed/cross-line effort in this project view.
- **Total allocation trend** shows the project's total allocated MM over time.
- **Allocation trend by role, employee, or line** shows how the selected breakdown contributes to the project's monthly trend. A one-month view may include the preceding months to provide context, and the chart may limit the displayed months for readability.

### Empty, zero, or surprising charts

- Empty chart: check the timeline, filters, report permission, project status, and whether any allocation matches the selected scope.
- 0% utilization: check whether capacity is zero before concluding that the team has no allocation.
- Missing department or line: check the employee department `SOURCE` value and the project's owner department, then refresh Allocation data.
- Unexpected internal/borrowed count: check whether the same employee is assigned to multiple projects and whether the selected view counts assignments rather than unique people.
- Missing actuals: check the active integration, sync status, employee/project mapping, date range, and whether the report refreshed after the correction.
- Different percentages across charts: check whether one chart uses capacity as its denominator, another uses total allocated MM, or the views use different timelines/status filters.
