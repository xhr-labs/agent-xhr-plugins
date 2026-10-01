---
name: exm-get-employee-expense-report
description: Drill into one employee's individual expense requests from the Expense Management report, with optional date-range and status filters.
side_effect: read
---

# Employee Expense Drill-down

## Intent: exm-get-employee-expense-report
### User request patterns
- show the expenses submitted by <name>
- break down this employee's expense total
- which expense claims make up that amount
- show <name> expense claims for this quarter
- list the approved expenses of one employee
- show the expense detail behind an employee report row

### Retrieval tags
- exm
- expense-management
- expense-reports
- employee-expenses
- expense-drilldown
- spending-detail

### Answer objective
Return one employee's individual expense requests for the requested period and status so the totals in the expense report can be explained line by line.

### Instructions
- This reads another employee's expenses and requires Expense Management reporting access. `permission_denied` means the caller is not authorized: say the report needs Expense Management admin or HR access and do not retry with other arguments.
- To read the caller's own expenses use `skills/exm/list_my_expenses` instead; this leaf is for a report drill-down.
- `--employee-id` takes a UUID only. Resolve it with `skills/exm/get_expense_report_overview` or `skills/employee/search_employees`; never guess an ID and never pass an employee name.
- Date filter: `--date-from` and `--date-to` in `YYYY-MM-DD`. For a relative period, run this exact command first and never invent the dates: `python skills/utils/resolve_date_range/scripts/resolve_date_range.py --expression "<DSL expression>" [--reference-date <YYYY-MM-DD>]`. Supported expressions include "today", "yesterday", "this week", "this month", "last month", "this year", and "last year". If the helper answers `Unsupported expression` (it does not understand quarters, "last 6 months", or "since <month>"), ASK the user for the exact start and end dates - never fill them in yourself.
- `--status` takes one expense status (`PENDING_APPROVAL`, `APPROVED`, `REJECTED`, `CANCELLED`, `REIMBURSED`).
- Present the result as a Markdown table: expense name, expense date, category, amount with currency, reimbursement amount, status. Render statuses in plain language, never the raw enum, and never sum different currencies together.
- Name the employee once above the table using the name from the report; never print employee IDs, expense IDs, or any UUID.
- When `meta.hasNext` is true, say the list is partial rather than presenting it as a complete total.
- An empty result is a normal answer: say the employee has no expense matching the filter.
- Do not repeat receipt contents, bank details, or any personal payment information beyond what the report returns.

### Required arguments
- `employee_id`: Employee UUID from the expense report overview or the employee directory.

### Optional arguments
- `date_from`: Period start (`YYYY-MM-DD`).
- `date_to`: Period end (`YYYY-MM-DD`).
- `status`: One expense status to filter on.
- `page`: Zero-based page number.
- `size`: Page size, 1-100, default 20.

### Execution
```text
python skills/exm/get_employee_expense_report/scripts/get_employee_expense_report.py --employee-id <uuid> [--date-from YYYY-MM-DD] [--date-to YYYY-MM-DD] [--status APPROVED] [--page N] [--size N]
```
