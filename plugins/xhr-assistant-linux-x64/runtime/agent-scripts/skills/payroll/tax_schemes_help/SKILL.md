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

### Direct answer
Open [Payroll -> Tax Schemes]({{payroll_tax_schemes_url}}).

Payroll tax schemes let payroll admins define tax-related rules, eligibility conditions, relief rules, and employee assignment behavior. The scheme form can include rule builders based on employee data, assigned employees, and excluded employees.

Deleting or archiving a tax scheme depends on usage. A scheme assigned to employees or used in payroll may be blocked from deletion or may only be archived so payroll history remains intact.
