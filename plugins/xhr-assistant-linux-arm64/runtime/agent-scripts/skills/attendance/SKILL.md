---
name: attendance
description: Attendance skill index for shifts, clock-in/out, timesheets, overtime, reports, and approval workflows. Use when the runtime or agent needs a guide to choose an attendance leaf skill.
---

# Attendance skill index

Use this file to choose the correct executable attendance skill.

## Navigation contract
- This file is a parent/index node only.
- Read the child `SKILL.md` entrypoint below to continue.
- Do not execute this directory as a script skill.
- Execute only the child leaf scripts referenced by the chosen leaf `SKILL.md` file.

## Child entrypoints
- skills/attendance/attendance_approvals_help/SKILL.md — Explain attendance approvals and pending timesheet review.
- skills/attendance/attendance_reports/SKILL.md — Fetch filtered attendance reports and employee report details.
- skills/attendance/attendance_setup_help/SKILL.md — Guide employees and HR/Admin through conditional Attendance setup.
- skills/attendance/attendance_troubleshooting_help/SKILL.md — Diagnose common Attendance errors and edge cases.
- skills/attendance/approve_timesheet_request/SKILL.md — Approve a pending attendance timesheet request.
- skills/attendance/assign_employees_to_shift/SKILL.md — Assign employees to an attendance shift.
- skills/attendance/clock_in_out_help/SKILL.md — Explain employee clock-in and clock-out behavior.
- skills/attendance/create_shift/SKILL.md — Create an attendance shift with working-hour targets.
- skills/attendance/detailed_timesheet_export/SKILL.md — Fetch exhaustive detailed timesheet rows for one resolved employee with identity and total validation.
- skills/attendance/device_imports_help/SKILL.md — Explain importing attendance-device CSV data.
- skills/attendance/get_shift/SKILL.md — Find attendance shifts by ID, name, or keyword.
- skills/attendance/generate_overtime_policy/SKILL.md — Draft and hand off an attendance overtime policy setup.
- skills/attendance/get_timesheet_requests/SKILL.md — List attendance timesheet requests with filters.
- skills/attendance/overtime_help/SKILL.md — Explain overtime policy setup and calculation behavior.
- skills/attendance/reject_timesheet_request/SKILL.md — Reject a pending attendance timesheet request.
- skills/attendance/remove_employee_from_shift/SKILL.md — Remove employees from an attendance shift.
- skills/attendance/shift_configuration_help/SKILL.md — Explain shift types, shift setup, and employee assignment.
- skills/attendance/submit_timesheets/SKILL.md — Submit one or more attendance timesheet entries.
- skills/attendance/timesheet_reports_help/SKILL.md — Explain attendance reports and report detail views.
