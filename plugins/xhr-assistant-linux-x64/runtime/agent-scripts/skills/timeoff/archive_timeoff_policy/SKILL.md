---
name: archive-timeoff-policy
description: Archive an active time-off policy so it is no longer assigned to new employees.
side_effect: write
---

# Archive Time-Off Policy

## Intent: archive-timeoff-policy
### User request patterns
- archive leave policy
- deactivate time off policy

### Retrieval tags
- timeoff
- archive-policy
- deactivate-policy

### Instructions
- **Input Verification Rule**:
  - `policy_id` is required (resolve via `get_timeoff_policies` if unknown).
- **Mandatory User Confirmation & Turn Boundary**:
  - Before executing `archive_timeoff_policy.py`, **ALWAYS** present a preview.
  - Ask the user: *"Do you confirm archiving this time-off policy?"*.
  - **STOP and wait for explicit user confirmation** in a subsequent turn before executing. **DO NOT execute the script in the same turn as presenting the preview.**

### Required arguments
- `policy_id`: UUID of the policy to archive.

### Execution
```text
python skills/timeoff/archive_timeoff_policy/scripts/archive_timeoff_policy.py --policy-id <UUID>
```
