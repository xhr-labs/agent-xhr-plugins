---
name: attendance-create-shift
description: Create an attendance shift with daily target hours in Attendance. Use when the user wants to create a new work shift/schedule, define working hours by weekday, or set up a default attendance shift, then execute skills/attendance/create_shift/scripts/create_shift.py after the final shift details are confirmed.
---

# Create shift

This file is an executable leaf skill entrypoint.

## Runtime entrypoint
- Execute `skills/attendance/create_shift/scripts/create_shift.py`.
- Do not search for another child skill under this directory.

## Intent Map

### User request patterns
- create a new attendance shift
- create a work shift named Office Hours
- create a shift called Night Shift
- set up a weekday shift 8 hours Monday to Friday
- create an attendance schedule with 8 hours on weekdays and 0 on weekends
- add a shift named Support Shift with custom daily target hours
- help me create a shift in attendance

### Retrieval tags
- attendance
- shift
- schedule
- configuration
- write-action

### Answer objective
Create a new attendance shift through `/v1/atd/shifts` after the final shift details are confirmed.

### Instructions
- This leaf performs a write action. Get explicit user confirmation after showing the final shift summary, and only then execute.
- Require `name` before execution.
- `description` is optional and defaults to an empty string.
- `apply_public_holiday_target_hours` is optional and defaults to `false`.
- For daily targets, accept either a fully custom per-day plan or default to:
  - Monday-Friday: 8 hours 0 minutes
  - Saturday-Sunday: 0 hours 0 minutes
- If the user provides partial weekday/weekend intent such as "8 hours on weekdays", expand it into the final per-day values before execution.
- Before execution, show the user a day-by-day summary for Monday through Sunday, including hours and minutes for each day.
- Do not fabricate creation success; rely on tool output.
- Do not mention internal tool names in the user-facing reply.

### Required arguments
- `name` — required shift name.

### Optional arguments
- `description`
- `apply_public_holiday_target_hours`
- `target_monday_hours`
- `target_monday_minutes`
- `target_tuesday_hours`
- `target_tuesday_minutes`
- `target_wednesday_hours`
- `target_wednesday_minutes`
- `target_thursday_hours`
- `target_thursday_minutes`
- `target_friday_hours`
- `target_friday_minutes`
- `target_saturday_hours`
- `target_saturday_minutes`
- `target_sunday_hours`
- `target_sunday_minutes`

### Execution
```text
python skills/attendance/create_shift/scripts/create_shift.py --name <required shift name> [--description <description>] [--apply-public-holiday-target-hours <true|false>] [--target-monday-hours <int>] [--target-monday-minutes <int>] [--target-tuesday-hours <int>] [--target-tuesday-minutes <int>] [--target-wednesday-hours <int>] [--target-wednesday-minutes <int>] [--target-thursday-hours <int>] [--target-thursday-minutes <int>] [--target-friday-hours <int>] [--target-friday-minutes <int>] [--target-saturday-hours <int>] [--target-saturday-minutes <int>] [--target-sunday-hours <int>] [--target-sunday-minutes <int>]
```
