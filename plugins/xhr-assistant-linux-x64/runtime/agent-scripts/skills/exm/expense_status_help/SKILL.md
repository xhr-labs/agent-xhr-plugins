---
name: exm-expense-status-help
description: Explain the expense statuses (pending, approved, rejected, canceled, reimbursed), what each one means for the employee, and which actions remain available, without calling tools.
---

# Expense Statuses and Actions

## Intent: exm-expense-status-help
### User request patterns
- what do the expense statuses mean
- what does pending mean on my expense
- difference between approved and reimbursed
- can I cancel an expense after it was approved
- can I edit an expense after submitting it
- what happens when my expense is rejected
- when do I get my money back for an expense

### Retrieval tags
- exm
- expense-management
- expense-status
- cancel-expense
- rejection
- reimbursement
- direct-answer

### Answer objective
Explain each expense status, what it means for the employee, and which actions are still possible in that state.

### Instructions
- Answer directly without calling executable tools.
- Use `skills/exm/list_my_expenses` or `skills/exm/get_expense` when the user asks about the state of a specific expense rather than the concept.
- Never promise a payment date; reimbursement timing follows the company's payout process, not the app.

### Direct answer
An expense in [My Expenses]({{expenses_my_expenses_url}}) carries one of five statuses.

- **Pending** - submitted and waiting for an approver. This is the only state in which you can cancel it, and the only state in which an approver can act on it.
- **Approved** - an approver accepted the claim. The money has not necessarily been paid yet.
- **Rejected** - an approver declined it, with a reason shown on the expense once the workflow completes.
- **Canceled** - you withdrew the request yourself.
- **Reimbursed** - the approved amount has been paid out through the company's reimbursement process.

Expenses cannot be edited after submission. If something is wrong, cancel the pending expense and submit a corrected one; once it has been approved, rejected, or reimbursed, cancelling is no longer possible and you need to raise it with your approver or finance team instead. A rejected expense is final too - submit a new expense rather than reopening the old one.

The app only offers the actions that are genuinely available on an expense, so the absence of a Cancel button means the expense has already left the pending state.
