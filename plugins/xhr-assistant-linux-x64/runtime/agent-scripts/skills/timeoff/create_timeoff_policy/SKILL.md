---
name: create-timeoff-policy
description: Create a basic Time Off policy with a leave type, location, annual allowance, accrual period, and effective date. Use the policy setup flow for advanced eligibility, carry-over, advance leave, seniority bonus, or retroactive configuration.
side_effect: write
---

# Create Time-Off Policy

## Intent: create-timeoff-policy
### User request patterns
- create leave policy
- set up time off policy
- add 14 days annual leave policy
- create a monthly leave accrual policy

### Retrieval tags
- timeoff
- create-policy
- policy-setup
- allowance-config

### Answer objective
Create a basic policy draft with explicit scope, allowance, accrual period, and start date, while routing advanced rules to the full setup flow.

### Instructions
- **Input Verification Rule**:
  - `name` is required.
  - `time_off_type_id` is required (resolve via `get_timeoff_types` if unknown).
  - `allowance`: Annual allowance in days. If the user gives a monthly amount, multiply it by 12.
  - `accrual_period`: `MONTHLY` or `YEARLY`.
  - Resolve the work location before creating the policy. If more than one active location exists, ask which one applies; do not silently choose one.
  - `effective_from` must be explicit. If the user did not provide a date, ask whether the policy should start today or on another date.
- **Mandatory User Confirmation & Turn Boundary**:
  - Before executing `create_timeoff_policy.py`, **ALWAYS** present a preview:
    - **Policy Name**: `<name>`
    - **Leave Type**: `<time_off_type_id>`
    - **Annual Allowance**: `<allowance> days`
    - **Accrual Period**: `<accrual_period>`
  - Ask the user: *"Do you confirm creating this time-off policy?"*.
  - **STOP and wait for explicit user confirmation** in a subsequent turn before executing. **DO NOT execute the script in the same turn as presenting the preview.**

### Required arguments
- `name`: Policy name.
- `time_off_type_id`: UUID of the leave type.
- `applied_location_id`: Work location for the policy.
- `effective_from`: Policy start date in `YYYY-MM-DD`.

### Optional arguments
- `allowance`: Annual allowance days (e.g. `14.0`).
- `accrual_period`: `MONTHLY` or `YEARLY` (default `MONTHLY`).
- `description`: Optional policy description.

### Execution
```text
python skills/timeoff/create_timeoff_policy/scripts/create_timeoff_policy.py --name "<name>" --time-off-type-id <UUID> --applied-location-id <UUID> --effective-from <YYYY-MM-DD> [--allowance 14.0] [--accrual-period MONTHLY]
```
