---
name: exm-expense-multi-currency-help
description: Explain multi-currency expenses - where the reimbursement currency comes from, when an exchange rate is required, how the reimbursement amount is calculated, and why totals are reported per currency.
---

# Multi-currency Expenses

## Intent: exm-expense-multi-currency-help
### User request patterns
- how do I claim an expense in a foreign currency
- why does the expense form ask for an exchange rate
- which currency will I be reimbursed in
- where does the exchange rate come from
- why is my reimbursement amount different from the amount I paid
- can I claim expenses in two currencies on one request
- why are expense totals split by currency

### Retrieval tags
- exm
- expense-management
- multi-currency
- exchange-rate
- reimbursement-currency
- foreign-currency
- direct-answer

### Answer objective
Explain how a foreign-currency expense is converted, who sets the rate, and how that shows up on the expense and in reports.

### Instructions
- Answer directly without calling executable tools.
- Never quote or estimate an exchange rate yourself; the rate is configured by the company or entered by the submitter.
- Use `skills/exm/get_expense` when the user asks which rate was actually applied to one of their expenses.

### Direct answer
Your **reimbursement currency** comes from your work location, not from the expense. When you submit in the same currency, nothing extra is asked.

When the expense currency differs, [Submit Expense]({{expenses_my_expenses_url}}) shows a multi-currency notice and asks for the **exchange rate** - expressed as 1 expense currency = n reimbursement currency. Where the company has configured a conversion rate for that currency pair, the form fetches it for you; otherwise you enter the rate you actually used. The form then calculates the reimbursement amount and shows it before you submit, and the rate must be greater than 0. That rate is part of what the approver reviews, so use the real rate from your payment, not a rounded guess.

The submitted expense keeps both sides: the original amount and currency you paid, and the reimbursement amount and currency you will be paid in. The expense detail shows the rate that was applied.

Because rates are recorded per expense rather than converted company-wide, expense reports keep each currency separate: an employee who claimed in two currencies appears with one total line per currency, and amounts in different currencies are never added into a single figure.
