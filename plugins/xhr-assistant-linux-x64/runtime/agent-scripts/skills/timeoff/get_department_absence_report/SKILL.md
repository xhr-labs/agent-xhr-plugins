---
name: get-department-absence-report
description: Find which department had the most approved absence requests, with a leave-type breakdown and stacked-bar chart.
side_effect: read
frontend_action: true
frontend_action_tool_name: exec
frontend_action_payload_mode: exec_path_args
frontend_action_execution_policy: always
---

# Get Department Absence Report

## Intent: get-department-absence-report
### User request patterns
- show which department has taken the most absences last year
- find the department with the most leave requests by type
- compare absence requests by department and leave type
- show a chart of absences by department

### Retrieval tags
- timeoff
- absence-report
- department-analytics
- leave-type-breakdown
- stacked-bar-chart

### Answer objective
Identify the department with the most absence requests for the requested period, explain the result in business language, and render the leave-type breakdown as a stacked bar chart.

### Instructions
- Always execute this tool for a department absence comparison request.
- Default to the previous calendar year when no period is given. Use the requested year, or a requested custom start and end date.
- Count distinct leave requests, not individual request days. For example, a three-day annual-leave request counts as one absence request.
- Default to approved requests because the user asked about leave that was taken. Use another status only when explicitly requested.
- The chart shows every department with matching requests in the period, stacked by leave type. Do not print, quote, or serialize its action payload or raw tool result in the response.
- State the top department and its request count. If the result is empty, explain that no matching absence requests were found; do not claim that the report failed.
- The tool supplies the final one-sentence answer with its chart action. Do not execute the report a second time after it returns.
- Do not expose internal IDs, endpoint paths, raw JSON, or implementation details.

### Optional arguments
- `year`: Calendar year (`YYYY`). Defaults to the previous calendar year.
- `start_date`: Custom range start (`YYYY-MM-DD`); requires `end_date`.
- `end_date`: Custom range end (`YYYY-MM-DD`); requires `start_date`.
- `status`: Request status. Defaults to `APPROVED`.

### Execution
```text
python skills/timeoff/get_department_absence_report/scripts/get_department_absence_report.py [--year <YYYY>] [--start-date <YYYY-MM-DD> --end-date <YYYY-MM-DD>] [--status APPROVED|PENDING|REJECTED|CANCELLED]
```
