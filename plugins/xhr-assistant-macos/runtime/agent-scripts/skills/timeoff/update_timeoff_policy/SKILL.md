---
name: update-timeoff-policy
description: Update the safe editable fields of an existing Time Off policy. Use the policy setup flow for advanced changes and check the policy status before proposing an update.
side_effect: write
---

# Update Time-Off Policy

## Intent: update-timeoff-policy
### User request patterns
- update leave policy
- change policy allowance
- edit time off policy
- change advance leave setting

### Retrieval tags
- timeoff
- update-policy
- edit-policy

### Answer objective
Update only fields supported by the basic policy action after checking policy status and confirming the intended change.

### Instructions
- **Input Verification Rule**:
  - `policy_id` is required (resolve via `get_timeoff_policies` if unknown).
  - At least one field to update must be specified.
- Scheduled policies allow full configuration edits. Active policies only allow name, description, effective end date, advance leave, and probation-request settings. Archived policies cannot be edited.
- Changing allowance, eligibility, accrual period, accrual year, timing, or proration on an active policy requires a new policy or an explicit retroactive workflow rather than this basic update action.
- This legacy update helper only exposes basic name, description, and allowance inputs. Do not use it to claim that advanced policy fields were updated; use the dedicated setup flow for those changes.
- **Mandatory User Confirmation & Turn Boundary**:
  - Before executing `update_timeoff_policy.py`, **ALWAYS** present a preview of changes.
  - Ask the user: *"Do you confirm updating this time-off policy?"*.
  - **STOP and wait for explicit user confirmation** in a subsequent turn before executing. **DO NOT execute the script in the same turn as presenting the preview.**

### Required arguments
- `policy_id`: UUID of the policy to update.

### Optional arguments
- `name`: New policy name.
- `allowance`: New annual allowance days.
- `description`: New description.

### Execution
```text
python skills/timeoff/update_timeoff_policy/scripts/update_timeoff_policy.py --policy-id <UUID> [--allowance 15.0] [--name "<name>"]
```
