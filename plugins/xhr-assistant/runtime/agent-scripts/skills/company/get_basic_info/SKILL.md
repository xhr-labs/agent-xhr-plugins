---
name: company-get-basic-info
description: Get the current company's basic profile, general information, and employee statistics. Use when the user asks for live current-company overview data such as company profile fields, employee counts, or high-level company summary information.
---

# Get Basic Info

Use this executable leaf when the workflow needs live basic information about the current company.

# Intent Map

## Intent: get-basic-info
### User request patterns
- show current company basic info
- get company profile
- show company overview
- what is the current company info?
- show company employee statistics
- get basic info for the current company
- show me information about our company
- my company info
- how many employees does our company have?
- show the current company profile
- what is the basic information of my company?
- Show me information about our company?

### Retrieval tags
- company
- basic-info
- profile
- company-overview
- employee-statistics
- current-company
- live-data

### Answer objective
Return the current company's live basic profile data and employee statistics.

### Instructions
- Use this leaf for live company-level overview questions.
- Use it when the user wants current company profile fields, company summary data, or employee statistics.
- Do not use this leaf for department catalog questions; use `skills/company/get_departments/SKILL.md` instead.
- Do not use this leaf for FAQ/help-center style questions such as values, USP, security explanation, scale explanation, or workspace how-to guidance; use the direct-answer company help leaves instead.
- Keep the answer grounded in the returned company data.

### Execution
- Run the company basic-info script via the restricted command-style exec surface:

```text
python skills/company/get_basic_info/scripts/get_basic_info.py
```

