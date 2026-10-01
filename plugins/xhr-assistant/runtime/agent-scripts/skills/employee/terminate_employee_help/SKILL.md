---
name: employee-terminate-employee-help
description: Explain how to terminate an employee safely in X-HR. Use when the user asks about employee termination, remaining time off, termination date, pending settlement, or the difference between termination and deactivation without requesting a live termination action.
---

# Terminate Employee Help

## Intent: employee-terminate-employee-help
### User request patterns
- terminate an employee
- offboard an employee with a termination date
- enter a pending settlement during termination
- review remaining time off before termination
- explain termination versus deactivation

### Retrieval tags
- employee
- termination
- offboarding
- settlement
- direct-answer

### Answer objective
Explain the employee termination flow and its safeguards.

### Instructions
- Answer directly without calling executable tools.
- Do not present termination as equivalent to deactivation or archive.

### Direct answer
1. Open [People]({{people_url}}) and find the employee.
2. Open the employee lifecycle actions and select **Terminate**.
3. Review the employee's remaining time-off balance when available.
4. Optionally choose a termination date. If it is omitted, the service uses the processing date.
5. Enter any pending settlement amount using the employee's compensation or work-location currency.
6. Review the warning and confirm termination.

Termination records the employee's exit. Deactivation temporarily disables an employee, while archive is the terminal action used to remove an eligible record from active People views.
