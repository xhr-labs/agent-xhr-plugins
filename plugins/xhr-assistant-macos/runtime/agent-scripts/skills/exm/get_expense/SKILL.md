---
name: exm-get-expense
description: Read one expense request in full - name, date, category, merchant, amounts, exchange rate, reimbursement, receipts, policy warnings, rejection reason, and the actions currently available on it.
side_effect: read
---

# Get Expense Detail

## Intent: exm-get-expense
### User request patterns
- show the details of this expense
- open my UAE Trip expense
- why was my expense rejected
- what is the reimbursement amount for this expense
- show the receipt attached to this expense
- check which policy warning this expense triggered
- show the exchange rate used on this expense
- what can I still do with this expense request

### Retrieval tags
- exm
- expense-management
- expense-detail
- receipt
- policy-warning
- rejection-reason
- reimbursement

### Answer objective
Return one expense request in full so the user can see its submitted details, money breakdown, receipts, policy result, and remaining actions.

### Instructions
- `--expense-id` takes a UUID only. Resolve it first with `skills/exm/list_my_expenses` (own expense) or `skills/exm/list_expense_approvals` (expense awaiting the caller's approval). Never construct, guess, or reuse a remembered UUID, and never pass an employee ID as an expense ID.
- `not_found` means the expense does not exist or the caller cannot see it. Say so and stop; do not retry with a different ID.
- Present the answer as short labelled lines or a two-column table: name, expense date, category, merchant, description, amount with currency, exchange rate (only when present and different from 1), reimbursement amount with currency, status, submitted on, receipts (file names and count).
- Render `status` in plain language, never the raw enum. When `rejectedReason` is present and the status is rejected, quote that reason verbatim; never invent a reason.
- Multi-item expenses return an `items` array. Summarize each line (line number, date, category, amount) and give the expense total; do not present one line as if it were the whole expense.
- `policyResult` carries the policy engine outcome. Report `BLOCK` as "blocked by policy" and `WARN` as a warning, list each violation message, and never restate a warning as a rejection.
- Receipts are listed by file name and document type only; this tool deliberately strips storage links. Tell the user to open the expense in [Expense Management]({{expenses_my_expenses_url}}) to preview or download a receipt, and never fabricate a download URL.
- Never print expense IDs, employee IDs, document IDs, or any other UUID in the reply.
- `availableActions` states what the caller may still do (`CANCEL`, `APPROVE`, `REJECT`). Offer only the actions listed there, then use `skills/exm/cancel_expense` or `skills/exm/manage_expense_approval`.

### Required arguments
- `expense_id`: Expense UUID from `list_my_expenses` or `list_expense_approvals`.

### Execution
```text
python skills/exm/get_expense/scripts/get_expense.py --expense-id <uuid>
```
