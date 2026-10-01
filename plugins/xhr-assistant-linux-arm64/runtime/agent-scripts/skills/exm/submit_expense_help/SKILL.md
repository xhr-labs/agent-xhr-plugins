---
name: exm-submit-expense-help
description: Explain how to submit an expense in the Expense Management app - required fields, receipts and AI scanning, multi-line expenses, and the validation rules that block submission - without calling tools.
---

# Submit an Expense (How-to)

## Intent: exm-submit-expense-help
### User request patterns
- how do I submit an expense
- what information do I need to claim an expense
- explain the expense submission form
- is a receipt required to submit an expense
- how do I add several receipts to one expense
- why can I not submit my expense
- how do I claim reimbursement for a purchase

### Retrieval tags
- exm
- expense-management
- submit-expense
- expense-form
- receipt-required
- validation
- direct-answer

### Answer objective
Explain the expense submission flow, the required fields, and the rules that stop a submission, so the user can complete the form themselves.

### Instructions
- Answer directly without calling executable tools.
- Do not claim an expense was submitted; use `skills/exm/submit_expense` when the user is ready to act.
- When the user is blocked, name the specific validation rule rather than describing the whole form again.

### Direct answer
Open [My Expenses]({{expenses_my_expenses_url}}) and choose **Submit Expense**. Upload the receipt or invoice first - drag and drop, or click the upload area; JPG, PNG, and PDF up to 5MB each are accepted. You can then **scan** an uploaded receipt so the merchant, date, amount, and category are filled in for you; scanned values never overwrite a field you already edited without asking, and the form warns you when several receipts disagree on currency, merchant, date, or category.

Fill in the rest: **Name** (for example "UAE Trip"), **Expense Date**, **Category**, **Amount** and **Currency**, plus the optional **Merchant** and **Description**. If your currency differs from your reimbursement currency, the form asks for the exchange rate you used and shows the calculated reimbursement; the approver reviews that rate.

Submission is blocked until the form is valid: a name, date, category, and currency are required, the amount must be greater than 0, an exchange rate must be greater than 0, at least one receipt is required, every uploaded receipt needs an amount, and any upload still running or failed must finish or be removed. Where expense policies are enabled, a policy marked as a hard block also stops submission and tells you which rule failed; a soft warning lets you submit and stays visible on the expense.

After submission the expense shows as **Pending** and moves into the approval workflow. You can still cancel it from My Expenses while it is pending.
