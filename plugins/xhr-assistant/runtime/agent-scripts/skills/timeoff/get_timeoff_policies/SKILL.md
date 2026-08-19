---
name: get-timeoff-policies
description: List configured time-off policies, annual allowances, accrual frequencies, and eligibility rules.
side_effect: read
---

# Get Time-Off Policies

## Intent: get-timeoff-policies
### User request patterns
- show time off policies
- list leave policies
- check policy allowance and accrual rules

### Retrieval tags
- timeoff
- policies
- policy-rules
- annual-allowance
- accrual-frequency

### Instructions
- Run `get_timeoff_policies.py` to view configured time-off policies.
- Can optionally filter by `time_off_type_id`.

### Optional arguments
- `time_off_type_id`: Filter by specific leave type UUID.

### Execution
```text
python skills/timeoff/get_timeoff_policies/scripts/get_timeoff_policies.py [--time-off-type-id <UUID>]
```
