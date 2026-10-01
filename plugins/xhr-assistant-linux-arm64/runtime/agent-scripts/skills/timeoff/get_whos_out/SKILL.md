---
name: get-whos-out
description: Query which employees are out of office, on leave today, this week, or in a specific date range across teams or departments.
side_effect: read
---

# Get Who's Out (Team Absences)

## Intent: get-whos-out
### User request patterns
- who is out today?
- who is on leave this week?
- show team absences / who's out
- check who is taking leave in Engineering department

### Retrieval tags
- timeoff
- whos-out
- absences
- out-of-office
- team-calendar
- leave-schedule

### Instructions
- Run `get_whos_out.py` to retrieve approved leaves for the specified date range.
- Defaults to 30 days ahead from today if dates are omitted.
- Can filter by department ID or employee name.

### Optional arguments
- `from_date`: Start date (`YYYY-MM-DD`).
- `to_date`: End date (`YYYY-MM-DD`).
- `department_id`: Department UUID.
- `employee_name`: Keyword to search by employee name.

### Execution
```text
python skills/timeoff/get_whos_out/scripts/get_whos_out.py [--from-date <YYYY-MM-DD>] [--to-date <YYYY-MM-DD>] [--department-id <UUID>] [--employee-name "<name>"]
```
