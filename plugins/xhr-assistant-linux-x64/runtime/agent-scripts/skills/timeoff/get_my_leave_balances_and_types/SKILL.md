---
name: timeoff-get-my-leave-balances-and-types
description: Fetch leave balances and related leave types for a year. Use when the user asks how many leave days remain, what leave types are available, or whether they have enough balance before planning or submission.
---

# Get My Leave Balances And Types

Use this executable leaf to inspect available leave balances and leave types for a target year.

# Intent Map

## Intent: get-leave-balances-and-types
### User request patterns
- I want to submit leave request
- Show my leave balance
- tôi muốn nghỉ 1 ngày phép hàng năm vào ngày 24/10/2025
- Tôi muốn nghỉ phép năm 2 ngày từ 5/11 đến 6/11/2025
- Tôi có thể xin nghỉ phép năm 1 ngày vào ngày 30/10/2025 được không?
- Tôi muốn dùng 1 ngày phép năm vào thứ Sáu tuần sau.
- Tôi muốn nghỉ không lương 1 ngày vào ngày 27/10/2025.
- Tôi có thể xin nghỉ không lương trong 3 ngày từ 1/11 đến 3/11/2025 không?
- Tôi bị ốm và muốn nghỉ 2 ngày từ 24 đến 25/10/2025.
- Tôi cần xin nghỉ 1 ngày vì bị sốt cao, là nghỉ ốm nhé.
- Tôi muốn nghỉ bù 1 ngày vào ngày 28/10/2025 vì đã làm thêm cuối tuần.
- Tôi muốn xin nghỉ thai sản từ 1/12/2025 trong 6 tháng.
- Tôi muốn nghỉ 1 ngày để chăm con ốm, đó là nghỉ chăm sóc gia đình.
- I’d like to take 2 days of annual leave from November 5th to 6th, 2025.
- Can I request one day of annual leave on October 30th, 2025?
- I want to use one day of annual leave next Friday.
- I’d like to take one day of unpaid leave on October 27th, 2025.
- Can I apply for 3 days of unpaid leave from November 1st to 3rd, 2025?
- I’m sick and would like to take 2 days of sick leave from October 24th to 25th, 2025
- I need to take one day off due to a high fever — it’s a sick leave.
- I’d like to take a compensatory leave on October 28th, 2025, since I worked over the weekend.
- I’d like to start my maternity leave on December 1st, 2025, for 6 months.
- I’d like to take one day of family care leave to look after my sick child.

### Retrieval tags
- timeoff
- balance
- leave-types
- eligibility

### Answer objective
Return the user's leave balances and available leave types for the requested year so the result can support planning or leave submission.

### Instructions
- Use the target year if the user provides one; otherwise default to the current year.
- Include both balances and related leave types when the script returns them.
- Use `requestable_balance` when deciding whether a request can fit the balance. It equals available balance plus the configured advance-leave limit when advance leave is enabled.
- Surface `advance_leave_enabled` and `advance_leave_limit_days` when explaining why the user can request more leave than their current available balance.
- If the user asks on behalf of another employee, only pass `employee_id` when policy and authorization allow it.
- Prefer this leaf before planning or submission when balance availability matters.
- Use the executable leaf rather than inferring balance data.

### Optional arguments
- `year` — optional year in `YYYY` format. If omitted, the script uses the current year.
- `employee_id` — optional employee id for authorized lookups.

### Execution
- Script entrypoint: `skills/timeoff/get_my_leave_balances_and_types/scripts/get_my_leave_balances_and_types.py`
- Use the restricted command-style `exec` surface with the explicit runtime-relative wrapper path and CLI flags when available.
