---
name: exm-expenses-overview-help
description: Explain what the Expense Management app is, which screens it has, and how an expense travels from submission through approval to reimbursement, without calling tools.
---

# Expense Management Overview

## Intent: exm-expenses-overview-help
### User request patterns
- what is the Expense Management app
- explain how expense management works
- how do expenses work in X-HR
- what can I do in the Expenses app
- explain the expense lifecycle
- who approves expenses in the company
- where do I find my expense claims

### Retrieval tags
- exm
- expense-management
- overview
- expense-lifecycle
- direct-answer

### Answer objective
Explain the purpose, screens, and end-to-end lifecycle of the Expense Management app so the user knows where to go and what happens next.

### Instructions
- Answer directly without calling executable tools.
- Do not claim any expense, approval, or configuration state; use the executable leaves for live data.
- Keep the answer to the modules the user asks about instead of listing every screen every time.

### Direct answer
[Expense Management]({{expenses_url}}) is the app employees use to claim work spending back and managers use to approve it. It has five areas: **My Expenses** for the expenses you submitted, **Approvals** for expenses waiting on your decision, **Reports** for spending totals across employees, **Categories** and **Policies** under Configuration, and **App Permissions** under App Settings. Which of them you see depends on your access.

An expense follows one path. You create it in My Expenses with a name, date, category, amount, and currency, and attach a receipt. On submission the platform's workflow engine routes it to the configured approvers, and the expense sits at **Pending**. An approver approves or rejects it from Approvals; a rejection carries a reason that you can read on the expense. You can withdraw your own expense with **Cancel** while it is still pending, but not after a decision, and a cancelled expense cannot be edited or resubmitted. An approved expense is paid out through the company's reimbursement process and then shows as **Reimbursed**.

Two configuration pieces shape what you can submit. Categories group spending (Travel, Meals, Accommodation) and every expense needs one. Expense policies, where enabled, check the expense against spending limits and requirements as you submit it, warning you or blocking the submission.
