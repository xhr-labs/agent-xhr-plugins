---
name: get-timeoff-reports
description: View and explain Time Off summary reports, including totals, employee or department breakdowns, date timelines, and day-count differences.
side_effect: read
---

# Get Time-Off Reports

## Intent: get-timeoff-reports
### User request patterns
- show time off report
- how many days of leave were taken this year?
- time off summary report for department
- why does the time off report total look different
- explain how Time Off report days are counted

### Retrieval tags
- timeoff
- reports
- analytics
- leave-summary
- department-metrics

### Answer objective
Retrieve a Time Off summary and explain its day totals, date scope, organization filters, and grouping in plain language.

### Instructions
- Run `get_timeoff_reports.py` to retrieve summary metrics and leave breakdown.
- The current report helper supports date range, timeline, grouping, department, leave type, and request-status filters. Do not present employee or team filters as available inputs to that helper.
- Reports count request-day hours and convert them using 8 hours = 1 day. Full day is normally 8 hours and a half-day is normally 4 hours.
- The report can present timelines by day, week, month, year, or a custom range, and can group results by employee, department, or company. A team is an organization filter, not a report grouping.
- If totals look wrong, verify date range, timezone, partial-day entries, leave type, and department before concluding that the balance is wrong. Use another available read-only capability only when it explicitly supports employee, team, or status filtering.

### Optional arguments
- `start_date`: Start date (`YYYY-MM-DD`).
- `end_date`: End date (`YYYY-MM-DD`).
- `timeline`: `DAY`, `WEEK`, `MONTH`, `YEAR`, or `RANGE`.
- `group_by`: `EMPLOYEE`, `DEPARTMENT`, or `COMPANY`.
- `department_id`: Department UUID.
- `time_off_type_id`: Leave type UUID.
- `status`: `PENDING`, `APPROVED`, `REJECTED`, or `CANCELLED`.

### Execution
```text
python skills/timeoff/get_timeoff_reports/scripts/get_timeoff_reports.py [--start-date <YYYY-MM-DD>] [--end-date <YYYY-MM-DD>] [--timeline DAY|WEEK|MONTH|YEAR|RANGE] [--group-by EMPLOYEE|DEPARTMENT|COMPANY] [--department-id <UUID>] [--time-off-type-id <UUID>] [--status PENDING|APPROVED|REJECTED|CANCELLED]
```
