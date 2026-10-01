---
name: delete-timeoff-policy
description: Permanently delete a time-off policy after explicit user confirmation.
side_effect: write
---

# Delete Time-Off Policy

## Intent: delete-timeoff-policy
### User request patterns
- delete leave policy
- remove time off policy

### Retrieval tags
- timeoff
- delete-policy
- remove-policy

### Instructions
- **Input Verification Rule**:
  - `policy_id` is required (resolve via `get_timeoff_policies` if unknown).
- **Mandatory Deletion Warning & Turn Boundary**:
  - Deleting a policy is destructive. **ALWAYS** show the deletion warning:
    - **Policy ID**: `<policy_id>`
    - **Warning**: *"Deleting this policy will permanently remove its rule configuration. This action cannot be undone."*
  - Ask the user: *"Are you sure you want to permanently delete this time-off policy?"*.
  - **STOP and wait for explicit user confirmation** in a subsequent turn before executing. **DO NOT execute the script in the same turn as presenting the warning.**

### Required arguments
- `policy_id`: UUID of the policy to delete.

### Execution
```text
python skills/timeoff/delete_timeoff_policy/scripts/delete_timeoff_policy.py --policy-id <UUID>
```
