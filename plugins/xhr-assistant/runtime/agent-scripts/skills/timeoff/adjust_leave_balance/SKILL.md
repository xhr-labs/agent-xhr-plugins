---
name: adjust-leave-balance
description: Manually adjust (credit or deduct) an employee's time-off leave balance with a reason note.
side_effect: write
---

# Adjust Leave Balance

## Intent: adjust-leave-balance
### User request patterns
- adjust leave balance for employee
- add 2 days to annual leave balance
- deduct 1 day from leave balance

### Retrieval tags
- timeoff
- adjust-balance
- manual-adjustment
- credit-leave
- deduct-leave

### Instructions
- **Input Verification Rule**:
  - `balance_id` is required (run `get_employee_leave_balances` to find the `balance_id` if unknown).
  - `amount`: Adjustment amount in days (positive number to add days, negative to deduct).
  - `reason`: Explanation or justification note for the manual adjustment.
- **Mandatory User Confirmation & Turn Boundary**:
  - Before executing `adjust_leave_balance.py`, **ALWAYS** present a preview:
    - **Balance ID**: `<balance_id>`
    - **Adjustment Amount**: `<+2.0 days or -1.0 day>`
    - **Reason / Note**: `<reason>`
  - Ask the user: *"Do you confirm adjusting this leave balance by [Amount] days?"*.
  - **STOP and wait for explicit user confirmation** in a subsequent turn before executing. **DO NOT execute the script in the same turn as presenting the preview.**

### Required arguments
- `balance_id`: UUID of the time-off balance record.
- `amount`: Adjustment amount (e.g. `2.0` or `-1.0`).

### Optional arguments
- `reason`: Note or justification for the adjustment.

### Execution
```text
python skills/timeoff/adjust_leave_balance/scripts/adjust_leave_balance.py --balance-id <UUID> --amount <float> [--reason "<reason>"]
```
