---
name: allocation-management-project-reports-help
description: Explain Allocation Management project and resource reports. Use when the user asks about project allocation reports, allocation history, resource summaries, workforce reports, or allocation dashboards.
---

# Project Allocation Reports Help

## Intent: allocation-management-project-reports-help
### User request patterns
- view project allocation reports
- show allocation history
- explain resource allocation reports
- review workforce resource summary
- filter allocation reports by department
- explain Source Line versus Allocated Line
- explain HR cost visibility in allocation reports
- compare project allocation with timesheets
- explain a project report chart

### Retrieval tags
- allocation-management
- reports
- project-allocation
- resource-summary
- source-line
- allocated-line
- cost
- direct-answer

### Answer objective
Explain available report surfaces, filters, definitions, permissions, and their business use.

### Instructions
- Answer directly without calling executable tools.
- Separate project reports from the Dashboard. Project reports focus on one project; Dashboard reports aggregate the company view.
- Explain project report timelines as Month, YTD, Whole project, or a custom range when the UI offers them.
- Explain that report totals are calculated from allocation data and capacity data; do not recalculate them from visible table rows or promise that a filter changes the monthly allocation list.
- Explain Source Line as the employee's department line and Allocated Line as the project owner's department line. Own-line and cross-line compare those two values.
- Mention that report filters can include department, project, employee type, employee, Source Line, Allocated Line, product line, work location, or job title where the selected report supports them.
- Explain that allocation status filters distinguish Planned, Tentative, and Unverified rows. A status filter changes the report population, not the saved allocation itself.
- Explain that HR cost views are permission-controlled and may be unavailable even when non-cost reports are visible. Do not expose payroll source or implementation details.
- Treat unresolved or unmapped dimensions as data-quality issues and recommend checking the source profile/project mapping rather than inventing a label.
- For questions about a chart's definition or formula, use `allocation_report_chart_glossary/SKILL.md`.

### Direct answer
Open [Allocation Reports]({{allocation_reports_url}}).

Allocation Management reports help leaders review project allocation, resource usage, workforce capacity, and actual-versus-plan effort. Project detail can include allocation reports and allocation history for a selected project.

Resource reports can summarize allocation by month and filter by dimensions such as department, project, employee type, employee, work location, job title, Source Line, Allocated Line, or product line where available. Use these reports to understand staffing coverage, utilization trends, planning risks, and cross-line demand.

The Dashboard can also compare allocation with imported actual work. Positive variance means actual work is higher than allocation; negative variance means actual work is lower. If no integration data has been imported or mapped, the report may be empty or incomplete.
