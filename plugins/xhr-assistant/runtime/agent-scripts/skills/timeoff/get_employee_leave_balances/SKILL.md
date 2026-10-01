---
name: get-employee-leave-balances
description: View leave balances (available, used, pending, total allowance) for any employee across all leave types.
side_effect: read
---

# Get Employee Leave Balances

## Intent: get-employee-leave-balances
### User request patterns
- check leave balance for employee John
- how many days of annual leave does Alex have left?
- view employee time off balance

### Retrieval tags
- timeoff
- employee-balance
- leave-balance
- available-days

### Answer objective
Return an employee's leave balances with the values separated clearly enough to explain what is credited, reserved, and requestable.

### Instructions
- Run `get_employee_leave_balances.py` to inspect leave balances for an employee.
- If only employee name is known, run `python skills/employee/search_employees/scripts/search_employees.py --name "<name>"` first to resolve `employee_id`.
- Report current, pending, available, and carry-over values separately. Do not describe current balance as the amount the employee can necessarily request.
- If the user asks why a value is wrong, follow the Time Off diagnosis workflow and inspect balance history and the matching policy.

### Optional arguments
- `employee_id`: UUID of the employee.
- `year`: Calendar year (default current year).

### Execution
```text
python skills/timeoff/get_employee_leave_balances/scripts/get_employee_leave_balances.py [--employee-id <UUID>] [--year <YYYY>]
```
