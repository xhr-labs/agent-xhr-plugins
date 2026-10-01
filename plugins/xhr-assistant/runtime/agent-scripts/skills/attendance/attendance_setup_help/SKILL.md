---
name: attendance-setup-help
description: Guide employees and HR/Admin through Attendance Tracking setup. Use when the user asks how to set up attendance, whether roster setup is required, or which manual or advanced roster mode to choose.
---

# Attendance Setup Help

## Intent: attendance-setup-help
### User request patterns
- set up attendance
- configure Attendance Tracking for employees
- how do I set up ATD
- do I need to set up a roster
- choose manual or advanced roster
- explain Attendance menus for employees and HR Admin
- start using attendance as an employee

### Retrieval tags
- attendance
- atd-setup
- employee-self-service
- hr-admin
- roster
- manual-roster
- advanced-roster
- conditional-setup
- direct-answer

### Answer objective
Give the shortest correct setup path for the user's role and scheduling model, with only valid ATD menu links.

### Instructions
- Answer directly for setup questions; do not call executable attendance tools.
- First separate employee self-service from HR/Admin setup.
- Do not tell an employee to configure shifts, policies, rosters, crews, or rotation patterns.
- Do not recommend roster setup unless the company uses workforce scheduling.
- Explain that ATD has two workforce scheduling modes: Manual and Advanced.
- Never link to a help-skill slug or invent an ATD route. Use only the placeholders in this leaf.

### Direct answer
Open [Attendance Tracking]({{attendance_url}}).

## If you are an employee

Open [My Attendance]({{attendance_my_attendance_url}}) to clock in or out, review your sessions, and add or submit timesheet entries when that access is enabled.

You do not need to set up a shift, attendance policy, overtime policy, roster, crew, or rotation pattern yourself. If My Attendance says that no shift is assigned, ask HR/Admin to assign you to the correct shift.

Use [Reports]({{attendance_reports_url}}) only if your role has report access. Use [Timesheet Approvals]({{attendance_approvals_url}}) only if you are an authorized reviewer.

## If you are HR/Admin

1. Open [Configuration]({{attendance_configuration_settings_url}}) and review the clock-in/out setting. Enable it only if employees should use the clock feature.
2. Open [Shifts]({{attendance_shifts_url}}) and create the working schedule employees will use. Assign employees here for standard shifts. Shift Work schedules are managed through workforce scheduling instead of direct employee assignment.
3. Open [Attendance Policies]({{attendance_attendance_policies_url}}) when the organization needs rules for attendance behavior.
4. Open [Overtime Policies]({{attendance_overtime_policies_url}}) and assign an overtime policy to shifts only when overtime should be calculated.
5. Choose the scheduling path only if the organization plans employee rosters:
   - **No roster:** stop after creating the shifts and any policies the organization needs. A roster is not required for ordinary shift-based attendance; employees can use My Attendance with their shift assignment.
   - **Manual:** choose Manual in [Configuration]({{attendance_configuration_settings_url}}), then use [Manual roster]({{attendance_manual_roster_url}}) to create and publish employee-by-date schedules. Crews and rotation patterns are not needed.
   - **Advanced:** choose Advanced in [Configuration]({{attendance_configuration_settings_url}}), then use the HR/Admin [Roster board]({{attendance_workforce_roster_url}}), [Crews]({{attendance_crews_url}}), and [Rotation patterns]({{attendance_rotation_patterns_url}}) for crew-based scheduling. Employees can use the separate [Roster Board]({{attendance_roster_board_url}}) when it is available to them.
6. Use [Reports]({{attendance_reports_url}}) to review attendance and overtime, [Timesheet Approvals]({{attendance_approvals_url}}) to review submitted timesheets, and [Device Imports]({{attendance_device_imports_url}}) when importing attendance-device CSV data.
7. Review [App Permissions]({{attendance_app_permissions_url}}) so employees, managers, and HR/Admin users have the intended access.

Roster mode is a scheduling choice, not a prerequisite for every Attendance customer. Configure only the path the organization actually uses.
