---
name: attendance-clock-in-out-help
description: Explain Attendance clock-in and clock-out behavior. Use when the user asks how employees clock in, clock out, view current session, or why a session cannot be closed.
---

# Clock In Out Help

## Intent: attendance-clock-in-out-help
### User request patterns
- clock in for attendance
- clock out from attendance
- view my current attendance session
- why can't I clock out
- why can't I clock in
- why does Attendance say no active shift
- why does Attendance say multiple shifts apply
- why is my session already closed
- explain attendance sessions

### Retrieval tags
- attendance
- clock-in
- clock-out
- sessions
- troubleshooting
- shift-assignment
- direct-answer

### Answer objective
Explain employee clock-in/out behavior, common error states, and when HR/Admin intervention is required.

### Instructions
- Answer directly without calling executable tools.

### Direct answer
Open [My Attendance]({{attendance_my_attendance_url}}).

Attendance Tracking can show the employee's current attendance state and session history where enabled. Employees clock in to start a session and clock out to close it.

Employees do not configure shifts or rosters from this page. If no active shift is assigned, HR/Admin must set up or assign the shift first.

If clock-in is unavailable, check for an already-open session, no active shift, an ambiguous shift assignment, approved time off, a device-clock problem, or missing access. If clock-out is unavailable, the session may already be closed, the current state may still be loading, a clock-out window may have been exceeded, a cooldown may apply, or the user may not have the required access. Managers should review the timesheet or session record if the employee's attendance state looks incorrect; employees should not create a duplicate session to work around the error.
