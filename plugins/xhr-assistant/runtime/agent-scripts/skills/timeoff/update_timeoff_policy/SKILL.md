---
name: update-timeoff-policy
description: Update an existing time-off policy's name, allowance days, or accrual schedule.
side_effect: write
---

# Update Time-Off Policy

## Intent: update-timeoff-policy
### User request patterns
- update leave policy
- change policy allowance
- edit time off policy

### Retrieval tags
- timeoff
- update-policy
- edit-policy

### Instructions
- **Input Verification Rule**:
  - `policy_id` is required (resolve via `get_timeoff_policies` if unknown).
  - At least one field to update must be specified.
- **Mandatory User Confirmation & Turn Boundary**:
  - Before executing `update_timeoff_policy.py`, **ALWAYS** present a preview of changes.
  - Ask the user: *"Do you confirm updating this time-off policy?"*.
  - **STOP and wait for explicit user confirmation** in a subsequent turn before executing. **DO NOT execute the script in the same turn as presenting the preview.**

### Required arguments
- `policy_id`: UUID of the policy to update.

### Optional arguments
- `name`: New policy name.
- `allowance`: New annual allowance days.
- `accrual_frequency`: New accrual frequency.
- `description`: New description.

### Execution
```text
python skills/timeoff/update_timeoff_policy/scripts/update_timeoff_policy.py --policy-id <UUID> [--allowance 15.0] [--name "<name>"]
```
