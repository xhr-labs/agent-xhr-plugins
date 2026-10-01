---
name: exm-manage-expense-approval
description: Approve or reject one expense request assigned to the caller, or approve every pending expense in the caller's queue, after explicit confirmation.
side_effect: write
idempotency: key
---

# Manage Expense Approval

## Intent: exm-manage-expense-approval
### User request patterns
- approve this expense request
- reject the expense claim from <name>
- approve the travel expense waiting for me
- reject this expense because the receipt is missing
- approve all pending expense requests
- yes, approve that expense
- decline the expense claim and tell them why

### Retrieval tags
- exm
- expense-management
- approve-expense
- reject-expense
- approve-all
- approval-decision
- write-action

### Answer objective
Execute exactly one confirmed approval decision - approve one expense, reject one expense with a reason, or approve the whole pending queue - and report the new status.

### Instructions
- **Never execute this script in a turn where the user asked not to act yet.** Wording such as "show me first", "do not decide yet", "just check", "preview it", "chua duyet", or "khoan duyet" means: write the preview, ask for confirmation, and call NO tool that writes. Executing in that turn is wrong even when every argument is already known and even when the preview is shown alongside it.
- `--action approve` and `--action reject` need `--expense-id` (UUID). Resolve it with `skills/exm/list_expense_approvals --view pending`; never guess an ID and never pass an employee ID.
- Before deciding, read the expense with `skills/exm/get_expense` and confirm that `availableActions` contains `APPROVE` or `REJECT`. When it does not, tell the user the item is no longer actionable and stop.
- A rejection requires `--comments`: the employee sees that reason when the workflow completes. Ask the user for the reason; never invent one. `--comments` is optional on an approval.
- **Mandatory user confirmation and turn boundary**:
  - Before executing, ALWAYS present a preview:
    - **Action**: `Approve` or `Reject`
    - **Expense**: `<name>` submitted by `<submitter>`
    - **Amount**: `<amount> <currency>`
    - **Reason / Comments**: `<text or "None">`
  - Ask: *"Do you confirm this decision?"*
  - STOP and wait for explicit confirmation in a later turn. DO NOT execute the script in the same turn as the preview.
- `--action approve_all` approves every expense currently pending in the caller's queue in one operation and cannot be undone. Before running it, call `skills/exm/list_expense_approvals --view count`, state the exact number of expenses that will be approved, list them if the user asks, and require a separate explicit confirmation. Never run it as a shortcut for a single approval, and never run it when the user only asked about one expense.
- After a successful run, report the new status of the affected expense (or the number approved), and say that reimbursement follows the company's payout process. Never print expense IDs or any other UUID.
- On a backend error, report the message and ask the user; do not retry with altered values. `permission_denied` means the caller is not an approver for that expense - stop and say so.

### Required arguments
- `action`: `approve`, `reject`, or `approve_all`.
- `expense_id`: Expense UUID; required for `approve` and `reject`, not used by `approve_all`.

### Optional arguments
- `comments`: Decision comment. Required for `reject`, optional for `approve`.
- `idempotency_key`: Optional idempotency key; the script generates one when omitted.

### Execution
```text
python skills/exm/manage_expense_approval/scripts/manage_expense_approval.py --action approve|reject --expense-id <uuid> [--comments "<text>"]
python skills/exm/manage_expense_approval/scripts/manage_expense_approval.py --action approve_all
```
