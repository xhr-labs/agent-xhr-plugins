---
name: attendance-shift-configuration-help
description: Explain Attendance shift configuration. Use when the user asks how to create shifts, choose Standard or Shift Work, assign employees, configure schedule types, or enable overtime on shifts.
---

# Shift Configuration Help

## Intent: attendance-shift-configuration-help
### User request patterns
- create an attendance shift
- explain Standard and Shift Work shifts
- assign employees to a shift
- remove employees from a shift
- configure vacation schedule type
- enable overtime for a shift
- why is a shift unavailable for rotation setup
- why can I not delete a shift
- why can an employee not submit attendance

### Retrieval tags
- attendance
- shifts
- schedule
- standard-shift
- shift-work
- employee-assignment
- direct-answer
- troubleshooting
- validation

### Answer objective
Explain shift setup, the two shift work-schedule types, and employee assignment behavior.

### Instructions
- Answer directly for help questions.
- Use shift executable leaves only when the user asks to create, assign, remove, or fetch live shift data.
- Do not link to internal help-skill paths; use the route placeholders below.

### Direct answer
Open [Shifts]({{attendance_shifts_url}}) to manage shifts. [Attendance Configuration]({{attendance_configuration_url}}) is the backward-compatible entry point and defaults to Shifts.

Attendance shifts define the working schedule and attendance expectations for employees. There are two shift work-schedule types:

- **Standard:** use daily or weekly target hours. HR/Admin can assign employees directly to the shift.
- **Shift Work:** use operational start/end timing and a timezone. Employee membership is managed through crews and rosters, so direct employee assignment is not part of this shift type.

Create shifts only when the organization needs them. A roster is optional and is not required for ordinary shift-based attendance.

Authorized users can configure schedule types such as vacation where supported and enable overtime when the shift should calculate extra work time. If overtime is enabled, select the appropriate policy from [Overtime Policies]({{attendance_overtime_policies_url}}).

If a Shift Work shift is unavailable for rotation setup, check that its operational start time, end time, and IANA timezone are complete. Shifts with linked timesheet entries cannot be deleted, and a required shift assignment can block employee timesheet creation. If the user wants to perform a real shift action, confirm the target shift, employees, dates, and required settings before using the executable attendance skill.
