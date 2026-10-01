---
name: exm-get-personal-development-budget-usage
description: Report how the organization is using its personal development budget (PDB, learning or training budget) - how many employees have used it, how many are in scope, how many expense requests were charged to it, and which categories and statuses are counted, optionally for a year or date range.
side_effect: read
---

# Personal Development Budget Usage

## Intent: exm-get-personal-development-budget-usage
### User request patterns
- show personal development budget usage overview
- check how many employees have used their personal development budget
- show PDB usage statistics for this year
- check personal development budget usage from 2026-01-01 to 2026-06-30
- show how many expense requests were charged to the personal development budget
- check learning and development budget usage across the company
- show training budget usage summary
- find out who has used the personal development budget so far

### Retrieval tags
- exm
- expense-management
- personal-development-budget
- pdb
- learning-budget
- training-budget
- budget-usage
- usage-report

### Answer objective
Return an organization-level summary of personal development budget usage for the requested period as a concise table: employees who used the budget, employees in scope, usage rate, expense requests counted, period, and the statuses and categories included.

### Instructions
- Always execute this read-only tool for a question about personal development budget (PDB), learning budget, or training budget usage or statistics. Never estimate or quote counts yourself.
- This is an organization-wide report. If the tool reports `permission_denied`, tell the user the report requires Expense Management admin or HR access and point them to their HR or finance owner; do not retry with other arguments.
- Period handling:
  - No period mentioned: run the tool WITHOUT date flags; the backend returns the overall (all-time) usage.
  - An explicit calendar year ("in 2026", "for 2025"): pass `--year <YYYY>`.
  - Explicit calendar dates: pass `--date-from YYYY-MM-DD --date-to YYYY-MM-DD` (convert `30/06/2026` to `2026-06-30`). Either bound may be passed alone for an open-ended range.
  - Any other relative phrase ("this month", "last month", "this year"): do not invent dates. Run this exact command first and pass the resolved start and end dates: `python skills/utils/resolve_date_range/scripts/resolve_date_range.py --expression "<DSL expression>"`. Supported expressions include "today", "yesterday", "this week", "this month", "last month", "this year", and "last year". If the helper answers `Unsupported expression` (it does not understand quarters, "last 6 months", or "since <month>"), ASK the user for the exact start and end dates - never fill them in yourself.
  - Never combine `--year` with `--date-from`/`--date-to`.
- If a date-filtered run fails with `personal_development_budget_usage_request_failed`, your reply MUST open with one sentence, in the user's language, saying that the report for the requested period (name the dates) is currently unavailable. You may then run the tool once more WITHOUT date flags and show the overall figures, but introduce them as all-time figures and make the period row of that table read "all time", never the requested range. Never present the overall figures as if they were filtered, and never silently swap the period.
- Always present the result as a normal Markdown table, even when every count is zero, with these rows: employees who used the budget, employees in scope (write "not configured" when `scoped_employee_count` is null), usage rate (omit when `usage_rate_percent` is null), expense requests counted, period (write "all time" when both dates are null), statuses counted, categories (list each category name with its expense request count, for example "Online courses (5)"; write "none recorded" when empty).
- Render statuses in plain language (for example "pending approval, approved, reimbursed"); do not show raw enum names such as `PENDING_APPROVAL`.
- When every count is zero, add one sentence below the table saying that no personal development budget spending has been recorded for the period. Do not describe that as an error.
- Privacy guardrail: this report is aggregate only. Never list, guess, or infer which employees used the budget, and never print employee IDs or UUIDs. If the user asks "who" used the budget, answer with the count and explain that per-employee detail is available to authorized users in the Expense Management app, not through this report.
- Do not expose endpoint paths, raw JSON, tool names, or implementation details.

### Optional arguments
- `year`: Calendar year (`YYYY`) to report on; expands to the full year. Cannot be combined with `date_from` or `date_to`.
- `date_from`: Period start (`YYYY-MM-DD`).
- `date_to`: Period end (`YYYY-MM-DD`). Must be on or after `date_from` when both are given.

### Execution
```text
python skills/exm/get_personal_development_budget_usage/scripts/get_personal_development_budget_usage.py [--year <YYYY>] [--date-from <YYYY-MM-DD>] [--date-to <YYYY-MM-DD>]
```
