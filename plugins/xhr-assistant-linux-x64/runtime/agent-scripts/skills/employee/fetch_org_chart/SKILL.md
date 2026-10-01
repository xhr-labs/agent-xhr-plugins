---
name: employee-fetch-org-chart
description: Fetch the company org chart with manager-report relationships and employee nodes. Use when the user asks to show the organization chart, reporting structure, or hierarchy across the company.
---

# Fetch Org Chart

Use this executable leaf when the user wants the company reporting hierarchy.

# Intent Map

## Intent: fetch-org-chart
### User request patterns
- show the org chart
- fetch the company org chart
- get the organization chart
- list the reporting hierarchy
- show the employee hierarchy
- find the company reporting structure
- display who reports to whom
- how many people do I manage?
- how many employees report to me?
- who reports to me?
- how many direct reports do I have?
- show my direct reports
- list my direct reports

### Retrieval tags
- employee
- org-chart
- hierarchy
- reporting-structure
- manager
- direct-reports

### Answer objective
Return the live org chart as nodes and edges so the caller can inspect employees, manager-report relationships, and hierarchy metadata.

### Instructions
- Use this leaf when the user wants the company-wide org chart or reporting hierarchy.
- Use this leaf when the user asks about direct reports or how many people they manage.
- Call the employee org chart endpoint with the fixed query values `depth=5`, `includeDeactivated=false`, and `maxNodes=1000`.
- Return the backend response without inventing employees or reporting relationships.
- Keep the result grounded in the returned `nodes`, `edges`, and `meta` fields.
- For questions about `who reports to me` or `how many people do I manage`, resolve the current employee from the runtime context and answer from the returned org-chart relationships and `number_of_direct_reports` when available.
- If the response is truncated, make that visible in the answer.
- Prefer this leaf over employee search flows when the user explicitly asks for an org chart or company hierarchy view.

### Supported arguments
- None.

### Execution
- Script entrypoint: `skills/employee/fetch_org_chart/scripts/fetch_org_chart.py`
- Example execution: `python skills/employee/fetch_org_chart/scripts/fetch_org_chart.py`
- Use the restricted command-style `exec` surface with the explicit runtime-relative wrapper path.
