---
name: allocation-management-find-overallocated-employees
description: Find employees whose planned allocation exceeds available capacity for a selected month or period.
side_effect: read
---

# Find Overallocated Employees

This file is an executable leaf skill entrypoint.

## Runtime entrypoint
- Execute `skills/allocation_management/find_overallocated_employees/scripts/find_overallocated_employees.py`.
- Do not search for another child skill under this directory.

## Intent: allocation-management-find-overallocated-employees
### User request patterns
- find overloaded employees
- show who is overallocated
- check who is currently over capacity
- find employees above 100 percent utilization
- identify overallocated employees this month
- show employees with zero capacity
- check overloaded employees by department
- check overloaded employees by project

### Retrieval tags
- allocation-management
- overloaded-employees
- overallocated
- capacity
- utilization
- resource-planning
- read-only-report

### Answer objective
Identify employees whose planned allocation is above their available capacity, while keeping employees with unavailable capacity in a separate list so they are not incorrectly labelled overloaded.

### Instructions
- This is a read-only report tool.
- On an initial request, propose the reporting period and filters, then ask for confirmation before execution.
- Default to the current calendar month in the user's timezone, with no filters.
- Support `MONTH`, `QUARTER`, `YTD`, and `RANGE`. For `RANGE`, require From month and To month.
- Treat an employee as overallocated only when allocated MM is greater than capacity MM, equivalent to utilization above 100 percent.
- Put employees with zero or unavailable capacity in `zeroCapacityEmployees`. Do not call them overloaded because a utilization percentage cannot be established.
- Aggregate rows for the same employee across source lines and projects before evaluating capacity. For one month, count capacity once per employee even when several source-line rows are returned.
- For a multi-month period, add each month's allocation and capacity, and include the monthly breakdown so the user can see when the overload occurred.
- Sort overallocated employees by utilization descending, then excess MM descending. Sort zero-capacity employees by allocated MM descending.
- Present employee name, department, source lines, allocated MM, capacity MM, utilization, excess MM, and the period or month breakdown when useful.
- Explain that MM means man-months when the user asks about the units. Do not expose internal identifiers, API paths, request data, tokens, database details, or service implementation.
- Distinguish no matching employees from unavailable capacity and from a failed report request. Do not claim that nobody is overloaded if the report request failed.
- After execution, state the selected period and filters used.

### Confirmation workflow
1. Propose the period and every non-default filter in user-facing labels.
2. Ask for explicit confirmation before execution, even though this is a read-only report.
3. If the user changes an option, show the revised selection and ask for confirmation again.
4. On a clear confirmation such as `confirm`, `yes`, `continue`, or `show it`, execute immediately with the confirmed values.

### Required arguments
- None. The month defaults to the current calendar month in the user's timezone.

### Optional arguments
- `month`: selected month in `YYYY-MM` format.
- `timeline`: `MONTH`, `QUARTER`, `YTD`, or `RANGE`; defaults to `MONTH`.
- `fromMonth`, `toMonth`: inclusive dates required for `RANGE`.
- `departmentId`, `employeeTypeId`, `workLocationId`, `jobTitleId`.
- `sourceLineKey`, `allocatedLineKey`, `productLineId`, `projectId`, `employeeId`.

### Execution
```text
python skills/allocation_management/find_overallocated_employees/scripts/find_overallocated_employees.py [--month <YYYY-MM>] [--timeline <MONTH|QUARTER|YTD|RANGE>] [--from-month <YYYY-MM> --to-month <YYYY-MM>] [filters]
```
