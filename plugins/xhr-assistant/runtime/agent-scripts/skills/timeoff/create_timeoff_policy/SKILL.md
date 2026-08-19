---
name: create-timeoff-policy
description: Create a new time-off policy specifying leave type, annual allowance, and accrual schedule.
side_effect: write
---

# Create Time-Off Policy

## Intent: create-timeoff-policy
### User request patterns
- create leave policy
- set up time off policy
- add 14 days annual leave policy

### Retrieval tags
- timeoff
- create-policy
- policy-setup
- allowance-config

### Instructions
- **Input Verification Rule**:
  - `name` is required.
  - `time_off_type_id` is required (resolve via `get_timeoff_types` if unknown).
  - `allowance`: Annual allowance in days (default `12.0`).
  - `accrual_frequency`: `MONTHLY`, `YEARLY_START`, `YEARLY_END`, `PER_PAY_PERIOD`.
- **Mandatory User Confirmation & Turn Boundary**:
  - Before executing `create_timeoff_policy.py`, **ALWAYS** present a preview:
    - **Policy Name**: `<name>`
    - **Leave Type**: `<time_off_type_id>`
    - **Annual Allowance**: `<allowance> days`
    - **Accrual Frequency**: `<accrual_frequency>`
  - Ask the user: *"Do you confirm creating this time-off policy?"*.
  - **STOP and wait for explicit user confirmation** in a subsequent turn before executing. **DO NOT execute the script in the same turn as presenting the preview.**

### Required arguments
- `name`: Policy name.
- `time_off_type_id`: UUID of the leave type.

### Optional arguments
- `allowance`: Annual allowance days (e.g. `14.0`).
- `accrual_frequency`: Accrual frequency (default `MONTHLY`).
- `description`: Optional policy description.

### Execution
```text
python skills/timeoff/create_timeoff_policy/scripts/create_timeoff_policy.py --name "<name>" --time-off-type-id <UUID> [--allowance 14.0] [--accrual-frequency MONTHLY]
```
