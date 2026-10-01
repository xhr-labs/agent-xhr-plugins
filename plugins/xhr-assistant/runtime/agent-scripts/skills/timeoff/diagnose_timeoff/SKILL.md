---
name: timeoff-diagnose-timeoff
description: Diagnose why a Time Off balance, accrual, policy, request, carry-over, or report result looks wrong, including eligibility and date edge cases. Use for explanation and read-only investigation; do not perform corrective writes.
---

# Diagnose Time Off

## Intent: diagnose-timeoff
### User request patterns
- why is my leave balance wrong
- why did this employee not receive leave days
- why was my time off request rejected
- why is a time off policy not accruing
- which leave policy applies to this employee
- why is carry-over missing or expired
- why can I not cancel approved leave
- why does the time off report show a different total
- explain pending versus available leave balance
- investigate a missing time off balance
- check a time off calculation
- troubleshoot time off setup

### Retrieval tags
- timeoff
- troubleshooting
- diagnosis
- balance
- accrual
- policy-resolution
- eligibility
- request-validation
- carry-over
- retroactive-recalculation
- reports
- read-only

### Answer objective
Find the most likely business cause of a Time Off result, explain it plainly, show the relevant evidence from read-only data, and recommend the smallest safe next step.

### Instructions
- This is an explanation and investigation skill. Do not perform balance edits, policy edits, recalculation, approvals, cancellations, or other writes.
- If live data is needed, use only the existing read-only Time Off lookups: employee balances, balance history, policies, leave requests, public holidays, and reports. Resolve an employee or leave type by name before asking for an internal identifier.
- Keep the investigation scoped to the employee, leave type, date range, and year named by the user. Do not assume the current year if another year is specified.
- Never expose API paths, UUIDs, database tables, class names, SQL, scheduled-job details, or internal error codes. Describe the result in user-facing terms.
- Explain the difference between:
  - current balance: days already credited to the employee;
  - pending balance: days reserved by submitted requests awaiting a decision;
  - available balance: current balance minus pending requests.
- When data is incomplete, say what cannot be confirmed and ask for the smallest missing detail, such as employee, leave type, dates, or location.

### Diagnosis workflow
1. Identify the exact employee, leave type, requested dates, balance year, and user expectation.
2. Check the employee balance and compare current, pending, available, carry-over, and expiry information.
3. Check the balance history for credits, approved leave deductions, cancellations, manual corrections, carry-over, expiry, and seniority additions.
4. Check the policy that applies to the employee and date: leave type, location, effective dates, employee type, employee status, gender, service-length rule, and probation restriction.
5. Check request dates against weekends, location holidays, explicit half-day selections, existing pending or approved requests, and the available balance.
6. Report the most likely cause, supporting evidence, and one safe next action. If more than one cause remains possible, rank them instead of guessing.

### Common diagnosis rules
- No balance or no new credit:
  - Confirm that the employee has a matching active policy for the leave type, location, dates, and eligibility rules.
  - A future policy does not credit days before its effective date.
  - A scheduled policy has not started accruing yet. An archived policy does not generate new days.
  - Monthly accrual at the end of a period is not due until that period ends; start-of-period accrual is credited at the beginning of the following period in the activity history.
  - An employee-start accrual year needs a valid employee start date.
  - A probationary employee may be prevented from requesting a type even when the policy exists. The employee-facing type list does not apply that filter to Admin and HR users, but the actual request permission should still be checked before concluding that they can submit on another employee's behalf.
  - Repeated accrual runs do not create duplicate credits for the same policy period.
- Balance is lower than expected:
  - First subtract pending requests from the current balance; pending days are reserved before approval.
  - Approved leave reduces the balance. Cancelling future approved leave restores it.
  - Expired carry-over is no longer available. Carry-over is used before the regular accrued balance.
  - Check for a manual correction, a carry-over limit, a policy end date, or a retroactive recalculation.
- Request says there is not enough balance:
  - Compare requested days with available balance, not the gross current balance.
  - If advance leave is enabled, the balance may go negative only down to the configured limit.
  - A request spanning dates with different advance-leave rules must be split into separate requests.
- Request duration is unexpected:
  - A date-range request counts weekdays and excludes public holidays for the employee location.
  - An explicit daily selection takes precedence: a full day counts as 1 day; morning, afternoon, and half day count as 0.5 day.
  - A range containing no eligible business day is rejected.
  - Pending and approved requests cannot overlap for the same employee; cancelled and rejected requests do not block the dates.
- Policy overlap or wrong policy:
  - Compare leave type, location, effective dates, and whether the eligibility rules can match the same employee.
  - Policies for mutually exclusive statuses or other conditions can coexist.
  - An open-ended policy with equivalent criteria may be ended the day before a replacement policy starts; a broader or conflicting policy must be resolved first.
  - An archived policy is not a current policy.
- Carry-over result:
  - Carry-over is processed at the end of the accrual cycle, subject to the policy limit.
  - An expiry setting can remove unused carry-over after its configured period.
  - If carry-over is disabled, unused positive balance is forfeited at cycle end.
  - A negative balance is carried into the next cycle only when advance leave is enabled for the governing policy.
- Retroactive result:
  - Retroactive setup is limited to the current calendar year in the setup flow.
  - By default, recalculation rebuilds generated accruals while preserving manual corrections, approved-leave history, and carry-over.
  - Resetting manual corrections or previously applied policy accruals is an explicit choice and can change the result substantially.
- Report mismatch:
  - Reports summarize request-day records, using 8 hours as 1 day.
  - Check the report date range, status filter, time zone, leave type, employee, department, and team filters.
  - A report grouped by employee, department, or company is not the same as a team grouping; team can be used as a filter.

### Response format
- Scope checked: employee, leave type, dates, and year.
- What the data shows: concise balance, policy, request, or report evidence.
- Likely explanation: one primary cause, with alternatives only when necessary.
- Next step: a safe read-only check or the appropriate user-facing setup screen. Do not silently make a correction.
