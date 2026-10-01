---
name: exm-cancel-expense
description: Cancel (withdraw) one of the caller's own pending expense requests after explicit confirmation, optionally recording a reason.
side_effect: write
idempotency: key
---

# Cancel Expense

## Intent: exm-cancel-expense
### User request patterns
- cancel my expense request
- withdraw the expense I submitted yesterday
- cancel the pending expense claim for the Dubai trip
- I submitted the wrong expense, cancel it
- yes, cancel that expense request
- stop the approval for my travel expense

### Retrieval tags
- exm
- expense-management
- cancel-expense
- withdraw
- expense-claim
- write-action

### Answer objective
Withdraw one specific pending expense request that belongs to the caller, after confirming exactly which expense is affected.

### Instructions
- **Never execute this script in a turn where the user asked not to act yet.** Wording such as "show me first", "do not cancel yet", "just check", "preview it", "chua huy", or "khoan huy" means: write the preview, ask for confirmation, and call NO tool that writes. Executing in that turn is wrong even when every argument is already known and even when the preview is shown alongside it.
- `--expense-id` takes a UUID only. Resolve it with `skills/exm/list_my_expenses`; never guess an ID. If more than one expense matches the user's wording, ask which one before continuing.
- Only the caller's own expenses can be cancelled, and only while the approval is still pending. Read the expense first with `skills/exm/get_expense` and check that `availableActions` contains `CANCEL`. When it does not, tell the user the expense can no longer be cancelled and why (already approved, rejected, reimbursed, or already cancelled).
- Cancelling is final: the approval request is withdrawn and the expense cannot be edited or resubmitted. Say this in the preview.
- `--reason` is optional. Pass it only when the user gives a reason; never invent one.
- **Mandatory user confirmation and turn boundary**:
  - Before executing, ALWAYS present a preview:
    - **Expense**: `<name>`
    - **Expense date**: `<YYYY-MM-DD>`
    - **Amount**: `<amount> <currency>`
    - **Reason**: `<reason or "None">`
  - Ask: *"Do you confirm cancelling this expense request?"*
  - STOP and wait for explicit confirmation in a later turn. DO NOT execute the script in the same turn as the preview.
- After a successful run, confirm that the expense is cancelled and that a new expense must be submitted if the user still wants reimbursement. Never print the expense ID or any other UUID.
- On a backend error, report the message and ask the user; do not retry with altered values.

### Required arguments
- `expense_id`: Expense UUID from `list_my_expenses`.

### Optional arguments
- `reason`: Cancellation reason supplied by the user.
- `idempotency_key`: Optional idempotency key; the script generates one when omitted.

### Execution
```text
python skills/exm/cancel_expense/scripts/cancel_expense.py --expense-id <uuid> [--reason "<text>"]
```
