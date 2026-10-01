---
name: exm-list-my-expenses
description: List the caller's own expense requests with status, category, date-range, and keyword filters, and resolve an expense name to its ID before a detail read, cancellation, or follow-up.
side_effect: read
---

# List My Expenses

## Intent: exm-list-my-expenses
### User request patterns
- show my expenses
- list my expense requests
- check the status of my expense claims
- show my pending expense approvals
- find my rejected expenses
- show expenses I submitted this month
- check my travel expense claims
- show my expenses from 2026-01-01 to 2026-03-31
- find my expense named UAE Trip
- how much have I claimed and not been reimbursed yet
- show my reimbursed expenses

### Retrieval tags
- exm
- expense-management
- my-expenses
- expense-list
- expense-status
- reimbursement
- claims

### Answer objective
Return the caller's own expense requests for the requested filters, with enough detail (name, date, category, amount, reimbursement amount, status) to answer the question or to pick one expense for a follow-up action.

### Instructions
- This leaf reads only the signed-in user's own expenses. For expenses awaiting the caller's approval use `skills/exm/list_expense_approvals`; for another employee's expenses use `skills/exm/get_employee_expense_report`.
- Status filter: pass `--status` once per status, or a comma-separated list. Valid values are `PENDING_APPROVAL`, `APPROVED`, `REJECTED`, `CANCELLED`, `REIMBURSED`. Map the user's wording: "pending" or "waiting" -> `PENDING_APPROVAL`, "paid" or "refunded" -> `REIMBURSED`, "withdrawn" -> `CANCELLED`.
- Date filter: `--date-from` and `--date-to` filter by expense date in `YYYY-MM-DD`. For a relative phrase ("this month", "last month", "this week"), run this exact command first and never invent the dates: `python skills/utils/resolve_date_range/scripts/resolve_date_range.py --expression "<DSL expression>" [--reference-date <YYYY-MM-DD>]`. Supported expressions include "today", "yesterday", "this week", "this month", "last month", "this year", and "last year". If the helper answers `Unsupported expression` (it does not understand quarters, "last 6 months", or "since <month>"), ASK the user for the exact start and end dates - never fill them in yourself. Read `skills/utils/resolve_date_range/SKILL.md` for the DSL if the expression is unclear.
- Category filter: `--category-id` takes a UUID only. Reuse a `category_id` that an earlier expense read already returned when it matches the category the user named; otherwise resolve the name with `skills/exm/list_expense_categories` first. Never guess a category ID.
- `--keyword` searches the expense name and merchant ONLY. Never pass a category name to `--keyword` as a stand-in for the category filter: a category is filtered with `--category-id`, and a keyword match on a category name is a coincidence, not a filter.
- Present the result as a Markdown table: name, expense date, category, amount (with currency), reimbursement amount, status. Render statuses in plain language ("Pending", "Approved", "Rejected", "Canceled", "Reimbursed"), never the raw enum.
- Never print expense IDs, employee IDs, or any UUID in the reply. Keep the ID only to drive a follow-up tool call.
- When `meta.hasNext` is true, say the list is partial and offer a narrower filter or the next page instead of claiming a complete total.
- When the list is empty, say plainly that no expense matches the filter; that is not an error.
- To act on one expense, read it first with `skills/exm/get_expense`, then use `skills/exm/cancel_expense`.

### Optional arguments
- `status`: Repeatable expense status filter (`PENDING_APPROVAL`, `APPROVED`, `REJECTED`, `CANCELLED`, `REIMBURSED`).
- `date_from`: Earliest expense date (`YYYY-MM-DD`).
- `date_to`: Latest expense date (`YYYY-MM-DD`).
- `category_id`: Expense category UUID from `list_expense_categories`.
- `keyword`: Free-text search over the expense name and merchant.
- `sort`: Backend sort expression, for example `expenseDate,desc`.
- `page`: Zero-based page number.
- `size`: Page size, 1-100, default 20.

### Execution
```text
python skills/exm/list_my_expenses/scripts/list_my_expenses.py [--status PENDING_APPROVAL] [--date-from YYYY-MM-DD] [--date-to YYYY-MM-DD] [--category-id <uuid>] [--keyword text] [--sort field,dir] [--page N] [--size N]
```
