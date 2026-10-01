---
name: exm-expense-approvals-help
description: Explain how expense approvals work - who gets the task, the pending queue and decision history, approve all, and how approval routing is configured through Workflows - without calling tools.
---

# Expense Approvals (How-to)

## Intent: exm-expense-approvals-help
### User request patterns
- how do expense approvals work
- who approves expenses in my company
- how do I approve an expense
- what does approve all do
- how do I change who approves expenses
- why do I not see any expense approvals
- do I have to give a reason when rejecting an expense

### Retrieval tags
- exm
- expense-management
- expense-approvals
- approval-workflow
- approve-all
- approver-routing
- direct-answer

### Answer objective
Explain the approval screen, the decision actions, and where approval routing is actually configured.

### Instructions
- Answer directly without calling executable tools.
- Do not claim an approval decision was made; use `skills/exm/manage_expense_approval` when the user is ready to decide.
- When the user wants to change who approves expenses, send them to the platform Workflows configuration, not to the Expense Management app permissions.

### Direct answer
[Approvals]({{expenses_approvals_url}}) shows the expense approval tasks assigned to you, split into **Wait for Approvals** (still pending your decision) and **Recent decisions** (what you already approved or rejected, searchable by submitter name). A counter next to the menu entry shows how many are pending, and the entry is hidden when you have no approval tasks at all.

Open an expense to see the submitter, the submitted details, the amounts, and the attached receipts before deciding. **Approve** accepts the claim; a comment is optional. **Reject** requires a reason - the employee sees it on their expense once the workflow completes. **Approve All** accepts every expense currently pending in your queue in one operation; the dialog states how many will be approved, and the action cannot be undone.

Approval routing is not configured inside Expense Management. The app publishes an `expense.submitted` event and the platform's Workflows engine decides who approves it; the default workflow sends the approval task to Admin and HR Manager roles. To change approvers, edit the expense approval workflow in Workflows. The Expense Management app permission screen controls who can see the app and its configuration, not who approves.
