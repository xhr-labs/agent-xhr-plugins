---
name: timeoff
description: Handle time-off workflows and guidance including leave balances, policies, carry-over, retroactive recalculation, maternity leave, leave requests, planning, approvals, and cancellations.
---

# Time Off Skill Tree

Navigate Time Off helpers categorized by functional domains:

## 1. Personal Leave & Balances (My Time Off)
- `skills/timeoff/submit_my_leave_request/SKILL.md` — Apply/submit personal leave with date range, leave type, and day type.
- `skills/timeoff/get_my_leave_balances_and_types/SKILL.md` — View caller's available, used, pending leave balances and available types.
- `skills/timeoff/get_leave_request/SKILL.md` — Search and inspect personal or team leave requests.
- `skills/timeoff/cancel_request/SKILL.md` — Cancel one or more pending leave requests after confirmation.
- `skills/timeoff/plan/SKILL.md` — Plan time off and inspect holiday impacts without submitting.
- `skills/timeoff/cancel_approved_leave_help/SKILL.md` — (Direct-answer only) Guidance on cancelling already-approved leave.
- `skills/timeoff/request_time_off_help/SKILL.md` — (Direct-answer only) General help on requesting time off.
- `skills/timeoff/maternity_leave_help/SKILL.md` — (Direct-answer only) Policy guidance for maternity and paternity leave.

## 2. Who's Out & Public Holidays
- `skills/timeoff/get_whos_out/SKILL.md` — Query who is out of office today, this week, or in a date range across departments.
- `skills/timeoff/get_public_holidays/SKILL.md` — List company public holidays and non-working days for a given year.

## 3. Approval Queue & Request Management
- `skills/timeoff/get_pending_requests/SKILL.md` — List all time-off requests waiting for manager or admin approval.
- `skills/timeoff/approve_request/SKILL.md` — Approve a specific leave request after confirmation.
- `skills/timeoff/reject_request/SKILL.md` — Reject a pending leave request with a mandatory reason note.
- `skills/timeoff/approve_all_pending_requests/SKILL.md` — Bulk approve all pending requests in the queue.

## 4. Reports & Analytics
- `skills/timeoff/get_timeoff_reports/SKILL.md` — View time-off metrics, total days taken, and employee breakdown across date ranges.

## 5. Configuration: Types, Policies & Balances
- `skills/timeoff/get_timeoff_types/SKILL.md` — List all configured leave types (paid, unpaid, code, color).
- `skills/timeoff/create_timeoff_type/SKILL.md` — Create a new leave type with color, paid status, and requirement settings.
- `skills/timeoff/update_timeoff_type/SKILL.md` — Update leave type name, color, or requirement settings.
- `skills/timeoff/delete_timeoff_type/SKILL.md` — Permanently delete a leave type after confirmation.
- `skills/timeoff/get_timeoff_policies/SKILL.md` — List leave policies, annual allowances, and accrual frequencies.
- `skills/timeoff/create_timeoff_policy/SKILL.md` — Create a new time-off policy specifying allowance and accrual schedule.
- `skills/timeoff/update_timeoff_policy/SKILL.md` — Update policy allowance days, name, or frequency.
- `skills/timeoff/archive_timeoff_policy/SKILL.md` — Archive a policy so it is no longer assigned to new staff.
- `skills/timeoff/delete_timeoff_policy/SKILL.md` — Permanently delete a time-off policy after confirmation.
- `skills/timeoff/get_employee_leave_balances/SKILL.md` — View leave balances for any employee across all leave types.
- `skills/timeoff/get_timeoff_ledger_entries/SKILL.md` — View balance transaction logs, accruals, and deductions for an employee.
- `skills/timeoff/adjust_leave_balance/SKILL.md` — Manually credit or deduct an employee's leave balance with a reason note.
- `skills/timeoff/generate_timeoff_policy/SKILL.md` — AI assistant to draft or generate compliant time-off policies.
- `skills/timeoff/configure_time_off_help/SKILL.md` — (Direct-answer only) Guidance on configuring time-off settings and rules.
- `skills/timeoff/timeoff_carryover_help/SKILL.md` — (Direct-answer only) Guidance on leave carryover rules and expiration.
- `skills/timeoff/timeoff_retroactive_policy_help/SKILL.md` — (Direct-answer only) Guidance on retroactive policy recalculation.

## Universal Design & Confirmation Principles (MANDATORY)
1. **No Implicit Assumptions**: If a user request is vague or lacks specific entities (e.g. "cancel leave", "reject request", "approve request"), **DO NOT guess, assume, or automatically select all requests**. List available options and ask the user to explicitly select target requests or parameters.
2. **Mandatory Input Verification & Preview**: Before calling ANY write/mutation script (submit, approve, reject, cancel, adjust balance, create/update/delete type or policy), ALWAYS present a clear, structured summary of all resolved parameters to the user.
3. **Mandatory Turn Boundary (STOP & Wait for User Confirmation)**: The agent MUST NOT call the execution script in the same turn as presenting the preview. The agent MUST ask for explicit confirmation (e.g., "Do you confirm ...?") and END its turn, waiting for the user's explicit approval (e.g., "yes", "confirm", "đồng ý") in a subsequent turn before executing.

## Suggested Navigation & Resolution Flows
- **Caller Balance Check**: Run `python skills/timeoff/get_my_leave_balances_and_types/scripts/get_my_leave_balances_and_types.py` to check available days before submitting.
- **Employee Balance Check**: When checking another employee, run `python skills/timeoff/get_employee_leave_balances/scripts/get_employee_leave_balances.py --employee-id <UUID>`.
- **Request Resolution**: When `request_id` is unknown, run `python skills/timeoff/get_leave_request/scripts/get_leave_request.py` or `python skills/timeoff/get_pending_requests/scripts/get_pending_requests.py` first.
- **Type Resolution**: Run `python skills/timeoff/get_timeoff_types/scripts/get_timeoff_types.py` to resolve valid `time_off_type_id`.
- **Policy Resolution**: Run `python skills/timeoff/get_timeoff_policies/scripts/get_timeoff_policies.py` to resolve valid `policy_id`.
