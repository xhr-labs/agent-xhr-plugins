---
name: company-get-departments
description: Retrieve the department list of the current company. Use when the user asks for live department data, department options, or the current organization's department structure.
---

# Get Departments

Use this executable leaf when the workflow needs the live department list of the current company.

# Intent Map

## Intent: get-departments
### User request patterns
- show the department list
- list company departments
- what departments does the company have?
- get all departments
- show me current company departments
- fetch department options for this company
- what are the departments in my company?
- list all current departments
- show the organization department structure

### Retrieval tags
- company
- departments
- organization
- org-structure
- current-company
- live-data

### Answer objective
Return the current company's live department list.

### Instructions
- Use this leaf only for live company-wide department listing.
- Use it when the user wants the current department catalog or department options.
- Do not use it for employee profile lookup.
- Do not use it for FAQ/help-center questions about how departments work in the product; use a direct-answer help leaf if that is what the user actually needs.
- If the user needs a specific employee instead of department structure, use employee-domain leaves.

### Execution
- Run the company departments script via the restricted command-style exec surface:

```text
python skills/company/get_departments/scripts/get_departments.py
```

