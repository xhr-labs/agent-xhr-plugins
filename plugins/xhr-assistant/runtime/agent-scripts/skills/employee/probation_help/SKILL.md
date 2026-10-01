---
name: employee-probation-help
description: Explain employee probation management in X-HR. Use when the user asks how to start probation, end probation early, record probation dates or notes, filter probationary employees, or automate probation reminders.
---

# Employee Probation Help

## Intent: employee-probation-help
### User request patterns
- start probation for an employee
- end employee probation early
- record a probation end date
- find employees currently on probation
- create a probation review reminder

### Retrieval tags
- employee
- probation
- workflow
- direct-answer

### Answer objective
Explain probation lifecycle actions and how probation dates can support automation.

### Instructions
- Answer directly without calling executable tools.

### Direct answer
- Open [People]({{people_url}}) and use **Start Probation** from the employee lifecycle menu. Enter the required planned end date, and optionally a start date and notes.
- Employees in probation receive the `PROBATIONARY` status and can be found with the People status filter.
- Use **End Probation** for a probationary employee. An actual end date is optional, while change notes are required.
- The Job tab shows saved probation details.
- A date-based workflow can use the probation end date to schedule review reminders before, on, or after that date.
