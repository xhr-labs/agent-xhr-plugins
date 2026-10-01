---
name: employee-search-employees
description: Search employees by name or keyword. Use when the user wants to find a colleague and the agent needs the employee skill instructions or the runtime script at skills/employee/search_employees/scripts/search_employees.py.
---

# Search employees

This file is an executable leaf skill entrypoint.

## Runtime entrypoint
- Execute `skills/employee/search_employees/scripts/search_employees.py`.
- Do not search for another child skill under this directory.

Run the employee search script via the restricted command-style exec surface:

```text
python skills/employee/search_employees/scripts/search_employees.py --name "<required name or keyword>"
```

## Intent Map

### User request patterns
- how can I search for an employee named John?
- show me the profile of John
- find employee John
- search for an employee by name
- look up an employee profile
- `name` is required and should be the plain employee name or keyword from the user.
- Do not invent employee IDs or profile details; rely on tool output.
- If the search returns no employees, report that the requested name was not found and ask for an exact name, email, or employee ID. Do not retry with guessed names, omit the required `--name`, or enumerate unrelated employees.
- If the search is ambiguous, ask the user to confirm the intended person before using the result in a later action.
- Do not invoke a downstream operation that requires an employee ID until the requested employee is unambiguously resolved.
- Do not mention internal tool names in the user-facing reply.
- Who is Alex?
