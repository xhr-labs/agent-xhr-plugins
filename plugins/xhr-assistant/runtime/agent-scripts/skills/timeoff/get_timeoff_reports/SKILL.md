---
name: get-timeoff-reports
description: View time-off analytics and summary reports including total days taken, employee breakdown, and department metrics.
side_effect: read
---

# Get Time-Off Reports

## Intent: get-timeoff-reports
### User request patterns
- show time off report
- how many days of leave were taken this year?
- time off summary report for department

### Retrieval tags
- timeoff
- reports
- analytics
- leave-summary
- department-metrics

### Instructions
- Run `get_timeoff_reports.py` to retrieve summary metrics and leave breakdown.
- Can filter by date range, department, and leave type.

### Optional arguments
- `start_date`: Start date (`YYYY-MM-DD`).
- `end_date`: End date (`YYYY-MM-DD`).
- `department_id`: Department UUID.
- `time_off_type_id`: Leave type UUID.

### Execution
```text
python skills/timeoff/get_timeoff_reports/scripts/get_timeoff_reports.py [--start-date <YYYY-MM-DD>] [--end-date <YYYY-MM-DD>] [--department-id <UUID>] [--time-off-type-id <UUID>]
```
