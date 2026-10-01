---
name: attendance-troubleshooting-help
description: Diagnose Attendance Tracking setup, clocking, timesheet, roster, overtime, report, import, and permission problems. Use when the user reports an ATD error, unexpected result, missing menu, missing shift, failed import, or confusing attendance value.
---

# Attendance Troubleshooting Help

## Intent: attendance-troubleshooting-help
### User request patterns
- troubleshoot an Attendance error
- why can I not clock in
- why can I not clock out
- why is my shift missing
- why is my timesheet rejected
- why can I not submit a timesheet
- why is my timesheet not approved
- why is overtime missing or incorrect
- why is my roster missing
- why can I not see an Attendance menu
- troubleshoot an attendance CSV import
- why is my attendance report empty

### Retrieval tags
- attendance
- atd
- troubleshooting
- edge-cases
- clock-in
- timesheets
- shifts
- roster
- overtime
- reports
- device-imports
- permissions
- direct-answer

### Answer objective
Triage the user's role, page, action, date, and exact error, then explain the most likely documented cause and the next safe check without inventing tenant state.

### Instructions
- Answer directly for explanation and troubleshooting questions; do not perform a write action.
- Ask for the exact error text, employee, work date, and page only when those details are needed to distinguish documented causes.
- Separate employee self-service problems from HR/Admin configuration and permission problems.
- Treat live tenant data, current permissions, current shift assignment, and current policy assignment as unknown unless returned by a permitted read flow.
- Never advise bypassing validation, approval, access controls, or a full-day time-off block.
- If the user asks to change data after diagnosis, route to the matching executable attendance leaf and follow its confirmation contract.
- Use only valid ATD destination placeholders; never invent a help-page URL.

### Direct answer
Start from [Attendance Tracking]({{attendance_url}}). Use the matching page below after identifying the role and symptom.

## Clock-in and clock-out problems

Open [My Attendance]({{attendance_my_attendance_url}}).

- **No active shift:** HR/Admin must assign an active shift for the day.
- **Multiple shifts apply:** the employee should not guess. HR/Admin must resolve the ambiguous shift assignment.
- **Shift not found:** the shift configuration or assignment needs HR/Admin review.
- **Already clocked in:** check today's current session before trying again.
- **Not clocked in:** clock-out cannot close a session that was never opened.
- **Today's session is closed:** a second clock-out is not available.
- **Approved time off today:** the clock action may be blocked by the approved leave.
- **Clock-out window exceeded:** follow the configured correction or manager-review process; do not create a duplicate session to work around it.
- **Device clock issue or a session spanning dates:** verify the device time and local date, then ask HR/Admin to review the session if it remains incorrect.
- **Rate limited or an earlier action is still being reconciled:** wait for the current result or refresh the page before retrying. Do not repeatedly submit the same action.

Employees do not configure shifts, policies, rosters, or permissions from My Attendance.

## Timesheet entry and submission problems

Open [My Attendance]({{attendance_my_attendance_url}}) for employee self-service or [Reports]({{attendance_reports_url}}) for an authorized manager or HR reviewer.

- The end time must be later than the start time.
- Entries for the same employee and date cannot overlap. Canceled entries do not participate in overlap validation.
- Where shift assignment is required by configuration, an employee must be assigned to a shift before creating an entry.
- An approved full-day time-off date remains blocked for attendance input. Partial-day leave remains visible and attendance input can remain available for the uncovered time.
- A canceled entry is immutable. Do not try to edit it; create or submit a valid replacement only if the workflow allows it.
- Only pending timesheet requests can normally be approved or rejected. An approved, rejected, or canceled request must follow its own correction or resubmission process.
- Managers can approve only requests within their authorized reporting scope. A missing request may be a scope, permission, status, or employee-resolution issue rather than an empty system.

## Approval problems

Open [Timesheet Approvals]({{attendance_approvals_url}}), or use [Reports]({{attendance_reports_url}}) and select Waiting for approval.

If an item is not available for approval, verify that it is still pending and that the reviewer has authority over the employee. Approve All is a long-running operation: its progress can include approval processing and overtime calculation. Do not start a duplicate bulk approval while the current operation is still processing or reconciling.

## Shift and roster problems

Open [Shifts]({{attendance_shifts_url}}) for static shift configuration or [Configuration]({{attendance_configuration_settings_url}}) for clock and roster-mode settings.

- A **Standard** shift uses daily or weekly target hours and supports direct employee assignment.
- A **Shift Work** shift requires operational start time, end time, and a valid IANA timezone when operational planning is used. Its employee membership is managed through workforce scheduling rather than direct shift assignment.
- A roster is optional for ordinary Standard-shift attendance. Do not configure Manual or Advanced scheduling unless the organization plans employee-by-date or crew-based schedules.
- **Manual** mode uses [Manual roster]({{attendance_manual_roster_url}}) and does not need Crews or Rotation patterns.
- **Advanced** mode uses the HR/Admin [Roster board]({{attendance_workforce_roster_url}}), [Crews]({{attendance_crews_url}}), and [Rotation patterns]({{attendance_rotation_patterns_url}}).
- If a user sees the wrong roster menu, check the persisted roster mode and whether the policy is still loading. If the policy read fails, the app intentionally falls back to Advanced so existing roster destinations remain reachable.
- A read-only user may see a selected mode but cannot change it. Missing setup actions can therefore be a write-permission issue.
- An incomplete operational shift can be unavailable in rotation-pattern selectors until its timing and timezone are fixed under Shifts.
- Employee Roster Board is read-only and shows published roster facts. HR/Admin management actions belong in the selected setup mode.
- Full-day time off remains locked in roster schedule editing. Clear actions apply only to editable populated roster cells; they do not delete the employee or alter the underlying time-off record.

## Overtime problems

Open [Overtime Policies]({{attendance_overtime_policies_url}}) to review policies and [Shifts]({{attendance_shifts_url}}) to check whether a shift has overtime enabled and which policy it uses.

- Overtime is optional. If no policy is assigned or overtime is disabled for the shift, no recognized overtime should be expected.
- In Approved reports, Overtime Hours represents the signed net balance. In Waiting for approval reports, it represents projected recognized overtime, so the values can differ before approval.
- Regular overtime is separate from rest-day and public-holiday overtime. Night overtime may have its own configured window.
- A negative balance indicates undertime or a negative time balance, not missing data.
- A cap warning means detected overtime was reduced by a configured cap. A cap-blocked result means no overtime was recognized because the cap was already reached.
- If a policy is already assigned to shifts, changing its rules may be forbidden. Create a new policy and assign it for future dates instead of altering the assigned rule in place.
- Retroactive overtime depends on the shift target, policy settings, attendance sessions, effective date, and backend calculation result. Do not infer a correction from the report total alone.

## Report problems

Open [Reports]({{attendance_reports_url}}).

Reports default to the Approved tab and the current month. To investigate unapproved data, select Waiting for approval. Annual mode represents approved attendance facts and month-by-month balance progression.

An empty table or empty section is a UI empty state; it is not proof that the company has no attendance records. Check the status tab, period, department, employee search, and permissions before concluding that data is missing. For a single employee, open the report detail and compare the date range, shift, leave, and approval status.

## Device import problems

Open [Device Imports]({{attendance_device_imports_url}}).

Upload, map the CSV columns, map device employees to X-HR employees, review backend-inferred rows, and submit only after validation issues are resolved. An import-wide active shift is optional; when it is not selected, each row can use the mapped `shift_code` column for shift resolution.

Do not resubmit blindly after a failed or uncertain import. First check the employee mapping, shift resolution, dates and times, duplicate or overlapping records, and the asynchronous job status. Device Imports does not require Manual or Advanced roster setup, but imported rows still need valid shift or schedule context.

## Missing menu or access problems

Open [App Permissions]({{attendance_app_permissions_url}}) if you are an authorized administrator.

Menu visibility is permission-based. Reports require report access; Shifts, Policies, Overtime, Configuration, and workforce setup require configuration or workforce access; Device Imports is shown to users with report or configuration edit access. Roster Board and employee self-service access are separate from HR/Admin setup access. If a menu is missing, identify the user's role and permission scope before treating the feature as unavailable.
