---
name: employee-search-manager
description: Find an employee's manager by using existing employee lookup flows and reading the returned line_manager field. Use when the user asks who manages someone or asks who their own manager is.
---

# Search manager

Use this executable/orchestration leaf when the user asks who someone's manager is.

# Intent Map

## Intent: search-manager
### User request patterns
- who is manager of
- my manager

### Retrieval tags
- employee
- manager
- line-manager
- reporting-line
- lookup

### Answer objective
Resolve the target employee and return the manager information from the available profile data, using the `line_manager` field as the source of truth.

### Instructions
- This is an orchestration leaf that relies on `search_employees` and the returned `line_manager` field.
- Do not use `get_my_profile` for manager lookup.
- If the user asks for `my manager`, resolve the current employee identity first using whatever employee name or current-user-to-employee resolution is already available in the runtime, then run `python skills/employee/search_employees/scripts/search_employees.py --name "<resolved current employee name or keyword>"`.
- If the user asks for another person's manager, run `python skills/employee/search_employees/scripts/search_employees.py --name "<employee name or keyword>"`.
- Use the `line_manager` field from the resolved employee result as the source of truth.
- If multiple employees match, ask the user to confirm the intended employee before answering.
- If no manager is present in the result, say that no line manager information was found.
- Do not invent manager names, IDs, or reporting relationships.
- Do not mention internal tool names in the user-facing reply.

### Execution
- Run the employee search flow:
  - `python skills/employee/search_employees/scripts/search_employees.py --name "<employee name or keyword>"`
