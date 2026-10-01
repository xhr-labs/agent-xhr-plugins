---
name: exm-submit-expense
description: Submit a new expense request for the caller after collecting the expense name, date, category ID, amount, and currency, and after explicit user confirmation.
side_effect: write
idempotency: key
---

# Submit Expense

## Intent: exm-submit-expense
### User request patterns
- submit an expense
- create an expense claim
- file a 250 USD taxi expense for yesterday
- claim my travel expense for the Dubai trip
- submit a meal expense of 40 USD at Starbucks
- request reimbursement for my hotel stay
- confirm and submit the expense with the selected category
- yes, submit that expense claim

### Retrieval tags
- exm
- expense-management
- submit-expense
- expense-claim
- reimbursement
- write-action

### Answer objective
Collect and validate every required expense input, confirm it with the user in a separate turn, then create the expense request and report the created expense and its status.

### Instructions
- **Never execute this script in a turn where the user asked not to submit.** Wording such as "do not send it yet", "show me the preview first", "just check", "draft it", "chua gui", or "khoan gui" means: write the preview, ask for confirmation, and call NO tool that submits. Executing the script in that turn is wrong even when every argument is already known and even when the preview is shown alongside it.
- Required inputs: `--name`, `--expense-date` (`YYYY-MM-DD`), `--category-id` (UUID), `--amount` (greater than 0), `--currency` (3-letter ISO code).
- Resolve `--category-id` with `skills/exm/list_expense_categories` and keep the matching category name visible in the preview. Never guess a category UUID. If the user's wording matches more than one category, ask which one before continuing.
- For a relative date ("yesterday", "last Friday"), run this exact command first and never invent the dates: `python skills/utils/resolve_date_range/scripts/resolve_date_range.py --expression "<DSL expression>" [--reference-date <YYYY-MM-DD>]`. Supported expressions include "today", "yesterday", "this week", "this month", "last month", "this year", and "last year". If the helper answers `Unsupported expression` (it does not understand quarters, "last 6 months", or "since <month>"), ASK the user for the exact start and end dates - never fill them in yourself.
- Currency and reimbursement: the reimbursement currency comes from the employee's work location. When `--currency` differs from it, the backend needs `--exchange-rate` (the rate of 1 expense currency to 1 reimbursement currency). Ask the user for the rate they used rather than inventing one, and state in the preview that the approver reviews it.
- Receipts cannot be uploaded through chat. Only pass `--documents-json` when the user supplies document IDs that already exist in the platform document store. If the company policy requires a receipt, the submission is rejected by the policy engine: tell the user to submit from [Expense Management]({{expenses_my_expenses_url}}), where the receipt can be uploaded and scanned, and do not retry.
- Use `--items-json` only for a genuinely multi-line expense, with one object per line (`lineNumber`, `expenseDate`, `categoryId`, `amount`, `currency`, optional `merchant`, `description`). The top-level name, date, category, amount, and currency still describe the expense as a whole.
- **Mandatory user confirmation and turn boundary**:
  - Before executing the script, ALWAYS present a preview:
    - **Name**: `<name>`
    - **Expense date**: `<YYYY-MM-DD>`
    - **Category**: `<category name>`
    - **Amount**: `<amount> <currency>`
    - **Exchange rate**: `<rate or "not needed">`
    - **Merchant / Description**: `<value or "None">`
  - Ask: *"Do you confirm submitting this expense?"*
  - STOP and wait for explicit confirmation in a later turn. DO NOT execute the script in the same turn as the preview.
- A request to only check, preview, or draft the expense is not a confirmation: do not submit in that turn.
- After a successful run, report the expense name, amount, and its new status (a submitted expense starts as pending approval and enters the approval workflow). Never print the created expense ID or any other UUID.
- On a backend validation error, report the message to the user and ask; do not retry with altered values. `permission_denied` means the user cannot submit expenses in this company - stop and point them to their HR or finance owner.

### Required arguments
- `name`: Expense name the user confirmed, for example `UAE Trip`.
- `expense_date`: Expense date (`YYYY-MM-DD`).
- `category_id`: Expense category UUID from `list_expense_categories`.
- `amount`: Amount greater than 0.
- `currency`: 3-letter ISO currency code, for example `USD`.

### Optional arguments
- `exchange_rate`: Rate from the expense currency to the reimbursement currency; required when they differ.
- `merchant`: Merchant name.
- `description`: Free-text description.
- `documents_json`: JSON array of `{"documentId": "<id>", "documentType": "EXPENSE_RECEIPT" | "EXPENSE_INVOICE"}`.
- `items_json`: JSON array of expense lines for a multi-line expense.
- `idempotency_key`: Optional idempotency key; the script generates one when omitted.

### Execution
```text
python skills/exm/submit_expense/scripts/submit_expense.py --name "<name>" --expense-date YYYY-MM-DD --category-id <uuid> --amount <number> --currency <ISO> [--exchange-rate <number>] [--merchant text] [--description text] [--documents-json '<json>'] [--items-json '<json>']
```
