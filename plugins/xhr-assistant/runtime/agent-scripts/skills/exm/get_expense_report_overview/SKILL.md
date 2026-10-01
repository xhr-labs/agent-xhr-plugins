---
name: exm-get-expense-report-overview
description: Read the Expense Management report - expense totals per employee broken down by currency into pending approval, approved, and reimbursed, or the flat per-expense rows behind the CSV export, with optional employee, department, date-range, and status filters.
side_effect: read
---

# Expense Report Overview

## Intent: exm-get-expense-report-overview
### User request patterns
- show the expense report
- how much has the company spent on expenses this quarter
- show expense totals by employee
- which employees have the highest expense claims
- show expense totals for the engineering department
- how much is still pending approval in expenses
- show approved but not yet reimbursed expenses
- show the expense summary from 2026-01-01 to 2026-06-30
- list the expenses that would be exported to CSV

### Retrieval tags
- exm
- expense-management
- expense-reports
- expense-totals
- spending-by-employee
- reimbursement-report

### Answer objective
Return per-employee expense totals for the requested scope and period split by currency, or the flat per-expense rows the CSV export is built from.

### Instructions
- Pick the view: `--view overview` (default) for per-employee totals, `--view export_candidates` for the flat per-expense rows (employee, department, expense date, expense, amount, status) that the app's CSV export would contain. Both views take the same filters.
- `--view export_candidates` does not produce a file. The CSV itself is downloaded from the app; never offer to generate, attach, or send it through chat.
- This is a management report over other employees' expenses and requires Expense Management reporting access. `permission_denied` means the caller is not authorized: say the report needs Expense Management admin or HR access, point them to their HR or finance owner, and do not retry with other arguments.
- The Reports screen is not exposed in every environment yet. Answer from the tool output and do not tell the user to click a Reports menu entry unless they say they can see it.
- Date filter: `--date-from` and `--date-to` in `YYYY-MM-DD`. For a relative period ("this month", "last month", "this year"), run this exact command first and never invent the dates: `python skills/utils/resolve_date_range/scripts/resolve_date_range.py --expression "<DSL expression>" [--reference-date <YYYY-MM-DD>]`. Supported expressions include "today", "yesterday", "this week", "this month", "last month", "this year", and "last year". If the helper answers `Unsupported expression` (it does not understand quarters, "last 6 months", or "since <month>"), ASK the user for the exact start and end dates - never fill them in yourself.
- `--employee-id` and `--department-id` take UUIDs only. Resolve an employee with `skills/employee/search_employees` and a department through the `company` domain; never guess an ID.
- `--status` takes one expense status (`PENDING_APPROVAL`, `APPROVED`, `REJECTED`, `CANCELLED`, `REIMBURSED`) and narrows the report to that status.
- Each row carries a `totals` array with one entry per currency. Never sum different currencies into a single number: report each currency on its own line or column.
- Present the result as a Markdown table: employee, department, currency, pending approval, approved, reimbursed. State the period covered above or below the table.
- Rows flagged `hasRejectedOrCancelledOnly` have no countable spend; say so rather than showing zeros as if they were real claims.
- Never print employee IDs, department IDs, or any UUID in the reply.
- When the report is empty, say plainly that no expense matches the filter for that period; that is not an error.
- For one employee's individual expenses, use `skills/exm/get_employee_expense_report`. CSV export is only available in the app; see `skills/exm/expense_reports_help`.

### Optional arguments
- `view`: `overview` (default) or `export_candidates`.
- `employee_id`: Employee UUID to narrow the report to one person.
- `department_id`: Department UUID to narrow the report to one department.
- `date_from`: Period start (`YYYY-MM-DD`).
- `date_to`: Period end (`YYYY-MM-DD`).
- `status`: One expense status to report on.
- `page`: Zero-based page number.
- `size`: Page size, 1-100, default 20.

### Execution
```text
python skills/exm/get_expense_report_overview/scripts/get_expense_report_overview.py [--view overview|export_candidates] [--employee-id <uuid>] [--department-id <uuid>] [--date-from YYYY-MM-DD] [--date-to YYYY-MM-DD] [--status APPROVED] [--page N] [--size N]
```
