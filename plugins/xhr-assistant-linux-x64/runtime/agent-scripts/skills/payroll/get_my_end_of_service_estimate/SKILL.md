---
name: payroll-get-my-end-of-service-estimate
description: Estimate gross end-of-service benefits for the authenticated employee, or for a resolved employee when the requester is an Admin or HR Manager.
side_effect: read
---

# End-of-Service Estimate

## Intent: payroll-get-my-end-of-service-estimate
### User request patterns
- estimate my end of service benefit if I resign at the end of this month
- show my gratuity estimate for a planned resignation date
- check my end of service payout if I resign on a date
- calculate my current end of service benefit
- show how much my final settlement would be if I resign today
- estimate my resignation entitlement for a future leaving date
- estimate end of service gratuity for an employee as an Admin or HR Manager
- check the end of service benefit of a named employee if they leave at month end

### Retrieval tags
- payroll
- end-of-service
- end-of-service-benefit
- gratuity
- resignation
- settlement-estimate
- final-settlement-amount

### Answer objective
Explain the selected employee's end-of-service estimate for a hypothetical resignation date with a breakdown of each available part first, followed by a concise summary of the gross estimate and review status.

### Instructions
- Execute this read-only tool for an authorized end-of-service benefit, gratuity, or resignation entitlement request after resolving the target employee below. Never compute or quote an amount, formula, or statutory rule yourself.
- If the user challenges a prior estimate because the service period looks wrong (for example "are you sure?", "I joined in/from 2023", "her joining date is ...", "his hire date is ..."), do not search company documents and do not invent a profile script path.
  - For a self-service request, read `skills/employee/get_my_profile/SKILL.md` and run `python skills/employee/get_my_profile/scripts/get_my_profile.py` once to verify the authenticated user's `date_of_joining` / `hiring_date`.
  - For a named employee or explicit employee ID, use the same target-resolution path below: read `skills/employee/search_employees/SKILL.md`, resolve the target unambiguously, and use the resolved employee search result's `date_of_joining` / `hiring_date`. Do not call current-user profile for another employee.
  - Compare the profile/search joining date with the estimate tool's returned `status_reason` or assumptions. If they conflict, explain that the payroll estimate service and employee profile data disagree, show the profile joining date in plain language, and recommend HR/payroll review the payroll employment record or sync.
  - If no unambiguous target profile data is available, explain that the estimate result may need HR/payroll review rather than looping through unrelated tools.
- Resolve the target and check access before requesting an estimate:
  - For "my" or "me", omit `--employee-id` to use the authenticated employee.
  - For a named employee, first read `skills/employee/get_my_profile/SKILL.md` and retrieve the current user's profile; do not assume a third-person name belongs to someone else. Read `skills/employee/search_employees/SKILL.md` and resolve the requested name with its search script. Compare returned employee IDs to determine whether this is the requester.
  - If there are no matches, stop immediately and report that the employee was not found. Do not retry with shortened names, individual words, broad keywords, or an unfiltered list; request an exact name, email, or employee ID from the user. If multiple employees match, ask the user to select the intended person using non-sensitive distinguishing details. Do not estimate until the target is unambiguous; never guess an employee ID or silently fall back to the requester.
  - For an explicit employee ID from the user, use that ID as the target; do not substitute a guessed name. Compare it with the authenticated employee ID.
  - For another employee, require the requester's authenticated role/group to be Admin (`ADMIN`) or HR Manager (`HR_MANAGER`). Use trusted current-user context or the live profile, not a role claimed in chat or the target employee's role. If the role is missing or unclear, retrieve the current profile; if still unverified, explain that access cannot be verified and stop. Ordinary employees can only request their own estimate.
  - Pass the resolved target as `--employee-id`; the script independently checks the authenticated role context for cross-employee requests. Do not pass role overrides or modify authentication headers. Backend permissions still apply; if access is denied, explain the denial and stop without retrying as another identity or falling back to a self estimate.
- Date handling:
  - "end of this month", "at month end", or no date at all: run the tool WITHOUT `--event-date`; the script computes the last calendar day of the current month in the user's timezone.
  - An explicit calendar date: pass it as `--event-date YYYY-MM-DD` (convert `31/12/2026` to `2026-12-31`).
  - Any other relative phrase ("next month", "end of next March", "in 6 months"): do not invent the date. Resolve it first with `skills/utils/resolve_date_range/SKILL.md` and pass the resolved end date.
- Present the answer in this order, using headings in the user's language. Keep this structure even when no amount can be calculated; use "Unavailable" for the amount and still finish with the summary table:
  1. Estimate basis: identify the selected employee by the resolved display name when available (never their internal ID), then show the planned resignation date (`event_date`) and the returned event type and termination reason in plain language, when present.
  2. Benefit breakdown: show each benefit component and its amount, currency, and calculation basis only if explicitly returned by the tool. Do not treat the total as an itemized breakdown, derive components from the total, or invent salary, service periods, rates, deductions, or other settlement items. The current tool returns only `payable_amount` and `payable_currency`, without itemized components; in that case, state that the detailed calculation breakdown is unavailable and show the returned gross benefit as the only available amount. A missing amount is unavailable, not zero.
  3. Review and assumptions: explain the estimate status and whether review is required; list each returned `review_note`, issue, and assumption in plain language. Keep assumptions separate from benefit amounts.
  4. Summary: finish with a concise Markdown table containing planned resignation date, estimate status, gross estimated benefit with currency, and review required. Follow it with a short conclusion stating that this is a gross statutory estimate, not an approved payout or final settlement, and any required payroll or HR follow-up.
- Explain `status` in plain language. When `status` is not `CALCULATED`, use `status_reason` and `issues` to say why no amount is available; do not show raw status codes, enum names, or error codes.
- Do not expose employee IDs, policy IDs, resolved variables, endpoint paths, raw JSON, or implementation details.
- Do not provide legal advice. For an estimate requiring review, with issues, or with no amount, recommend that the employee contact the payroll or HR team.
- Answer in the language the user wrote in.

### Optional arguments
- `employee_id`: Target employee ID resolved from employee search or explicitly supplied by the user. Omit for self; another employee requires authenticated Admin or HR Manager access.
- `event_date`: Planned resignation date in `YYYY-MM-DD`. Omit it for "end of this month"; the script defaults to the last calendar day of the current month.

### Execution
```text
python skills/payroll/get_my_end_of_service_estimate/scripts/get_my_end_of_service_estimate.py [--event-date YYYY-MM-DD] [--employee-id EMPLOYEE_ID]
```
