---
name: get-timeoff-policies
description: List configured Time Off policies and explain their status, allowance, accrual, eligibility, effective dates, and carry-over rules.
side_effect: read
---

# Get Time-Off Policies

## Intent: get-timeoff-policies
### User request patterns
- show time off policies
- list leave policies
- check policy allowance and accrual rules
- which policy applies to this employee
- inspect a policy that is not accruing

### Retrieval tags
- timeoff
- policies
- policy-rules
- annual-allowance
- accrual-frequency

### Answer objective
Show the configured policies and identify the rules that determine whether a policy is active, applicable, and accruing.

### Instructions
- Run `get_timeoff_policies.py` to view configured time-off policies.
- Can optionally filter by `time_off_type_id`.
- When explaining a policy, check its status, leave type, location, effective dates, eligibility conditions, allowance, accrual period and timing, proration, carry-over, advance leave, and probation setting.
- Treat `SCHEDULED` as not started, `ACTIVE` as accruing, and `ARCHIVED` as closed to new accrual. If a policy is shown as activating or appears stuck, use the Time Off diagnosis workflow instead of claiming that it is active.
- If the user asks why a policy does not apply or accrue, compare the employee's location, type, status, gender, service length, start date, and the policy's effective dates.

### Optional arguments
- `time_off_type_id`: Filter by specific leave type UUID.

### Execution
```text
python skills/timeoff/get_timeoff_policies/scripts/get_timeoff_policies.py [--time-off-type-id <UUID>]
```
