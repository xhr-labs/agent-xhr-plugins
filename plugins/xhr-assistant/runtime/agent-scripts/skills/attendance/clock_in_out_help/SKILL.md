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
- explain attendance sessions

### Retrieval tags
- attendance
- clock-in
- clock-out
- sessions
- direct-answer

### Answer objective
Explain employee clock-in/out behavior and common state constraints.

### Instructions
- Answer directly without calling executable tools.

### Direct answer
Attendance Tracking can show the employee's current attendance state and session history where enabled. Employees clock in to start a session and clock out to close it.

If clock-out is unavailable, the session may already be closed, the current state may still be loading, a cooldown may apply, or the user may not have the required access. Managers should review the timesheet or session record if the employee's attendance state looks incorrect.
