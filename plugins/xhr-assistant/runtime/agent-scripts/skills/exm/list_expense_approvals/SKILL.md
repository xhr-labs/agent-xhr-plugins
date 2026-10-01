---
name: exm-list-expense-approvals
description: Read the caller's expense approval workload - expenses waiting for their decision, their recent approval or rejection history, or just the pending and total counters.
side_effect: read
---

# List Expense Approvals

## Intent: exm-list-expense-approvals
### User request patterns
- show expenses waiting for my approval
- how many expense requests do I need to approve
- list my pending expense approval tasks
- show the expenses I approved recently
- show my recent expense approval decisions
- which expense claims did I reject last month
- do I have any expense approvals pending
- show the expense approval queue

### Retrieval tags
- exm
- expense-management
- expense-approvals
- approval-queue
- approval-history
- pending-approvals
- approver

### Answer objective
Return the expenses assigned to the caller for a decision, the caller's past decisions, or the approval counters, with enough detail to pick one expense for an approve or reject action.

### Instructions
- This leaf reads approval tasks assigned to the signed-in user. It is not the caller's own expense list (`skills/exm/list_my_expenses`) and not an organization-wide report (`skills/exm/get_expense_report_overview`).
- Pick the view:
  - `--view pending` (default): expenses currently waiting for the caller's decision.
  - `--view history`: the caller's recent decisions, filterable with `--status` and `--keyword`.
  - `--view count`: the pending and total counters only. Use this whenever the answer is a number or a yes/no - "how many approvals do I have", "do I have any waiting", "is there anything to approve" - because it is the cheapest call. Only switch to `--view pending` once the user asks to see the items themselves.
- `--status` applies to the history view only, and takes `PENDING_APPROVAL`, `APPROVED`, `REJECTED`, `CANCELLED`, or `REIMBURSED` (repeatable or comma-separated).
- `--keyword` on the history view searches the submitter name.
- Present pending items as a Markdown table: submitter, expense name, expense date, amount with currency, reimbursement amount. For history, add the decision (approved or rejected) and the decision date. Render statuses in plain language, never the raw enum.
- Never print expense IDs, employee IDs, or any UUID in the reply; keep an ID only to drive a follow-up call.
- Approval routing is owned by Workflows, so the queue only shows tasks actually assigned to the caller. An empty queue is a normal result, not an error: say there is nothing waiting.
- When `meta.hasNext` is true, say the list is partial rather than reporting it as the full queue.
- To decide on an item, read it with `skills/exm/get_expense`, then act with `skills/exm/manage_expense_approval`.

### Optional arguments
- `view`: `pending` (default), `history`, or `count`.
- `status`: History view only. Repeatable expense status filter.
- `keyword`: History view only. Free-text search over the submitter name.
- `page`: Zero-based page number (pending and history views).
- `size`: Page size, 1-100, default 20.

### Execution
```text
python skills/exm/list_expense_approvals/scripts/list_expense_approvals.py [--view pending|history|count] [--status APPROVED] [--keyword text] [--page N] [--size N]
```
