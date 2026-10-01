---
name: payroll-tax-schemes-help
description: Explain Payroll tax schemes. Use when the user asks how to create tax schemes, configure eligibility rules, assign employees, exclude employees, use relief rules, or delete/archive tax schemes.
---

# Tax Schemes Help

## Intent: payroll-tax-schemes-help
### User request patterns
- create a tax scheme
- configure tax scheme eligibility
- assign employees to a tax scheme
- exclude employees from tax scheme eligibility
- delete or archive a tax scheme

### Retrieval tags
- payroll
- tax-schemes
- eligibility
- assigned-employees
- direct-answer

### Answer objective
Explain tax scheme configuration and guarded lifecycle behavior.

### Instructions
- Answer directly without calling executable tools.
- Do not provide legal or jurisdiction-specific tax advice.
- For setup, exclusion, archive, or deletion changes, explain the effect and ask for confirmation before a data-changing action is executed.

### Direct answer
Open [Payroll -> Tax Schemes]({{payroll_tax_schemes_url}}).

Payroll tax schemes let payroll admins define tax-related rules, eligibility conditions, relief rules, and employee assignment behavior. The create flow covers **Details**, **Tax Base**, **Rates & Thresholds**, **Tax Reliefs**, **Eligibility**, and **Review & Test**. Choose the Work Location and effective dates, then choose taxable income or gross income as the base. Brackets must start at zero, remain continuous, and end with one open-ended final bracket. Choose the flat-rate or progressive strategy shown in the form.

Eligibility rules are evaluated against employee data, Work Location, and effective dates. Employees can also be explicitly excluded, and the scheme detail view shows both assigned and excluded employees. If tax is missing from a pay run, check the pay run tax toggle, the Pay Structure tax setting, the scheme's effective dates, the employee's eligibility result, and any exclusion.

Deleting or archiving a tax scheme depends on usage. A scheme assigned to employees, used by an active pay run, or retained for payroll history may be blocked from deletion or may only be archived so payroll history remains intact. Archiving prevents new assignment while preserving the historical record.
