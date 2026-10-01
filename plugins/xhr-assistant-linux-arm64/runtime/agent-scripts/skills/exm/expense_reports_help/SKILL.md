---
name: exm-expense-reports-help
description: Explain the Expense Management reports - per-employee totals by currency, the employee drill-down, the filters, and the CSV export - without calling tools.
---

# Expense Reports (How-to)

## Intent: exm-expense-reports-help
### User request patterns
- what is in the expense report
- how do I export expenses to CSV
- can I filter the expense report by department
- how do I see what an employee claimed
- why are expense totals shown per currency
- who can see the expense reports
- where do I find company expense totals

### Retrieval tags
- exm
- expense-management
- expense-reports
- csv-export
- reporting-access
- direct-answer

### Answer objective
Explain what the report shows, how it is filtered, and how the export works, including its access requirements.

### Instructions
- Answer directly without calling executable tools.
- Use `skills/exm/get_expense_report_overview` and `skills/exm/get_employee_expense_report` when the user wants the numbers rather than an explanation.
- The Reports screen is not exposed in every environment. Do not insist the user can see the menu entry; describe the report and offer to read the data instead.
- The CSV file is produced by the app and downloaded in the browser. Never offer to generate, attach, or send the file through chat.

### Direct answer
[Reports]({{expenses_reports_url}}) summarizes expense spending by employee. Each row is one employee with their department, and the totals are split **per currency** into pending approval, approved, and reimbursed - amounts in different currencies are never added together, so an employee who claimed in two currencies appears with one line per currency. Employees whose expenses were all rejected or cancelled are flagged as having no countable spend.

The report can be filtered by employee, department, date range, and status, and you can open an employee to drill into the individual expense requests behind their totals.

**Export CSV** produces a file of the expenses currently selected: select all, or pick individual rows, then export. The file is downloaded by your browser from the app.

Reports read other employees' expenses, so they require Expense Management reporting access. If you cannot see the screen or the data, ask an Expense Management admin or your HR or finance owner for access.
