---
name: payroll-statutory-schemes-help
description: Explain Payroll statutory schemes, contribution types, programs, eligibility, and employee enrollment. Use when the user asks where statutory schemes are managed, who can edit enrollment, why schemes are read-only, or how payroll and compliance affect scheme availability.
---

# Statutory Schemes Help

## Intent: payroll-statutory-schemes-help
### User request patterns
- manage employee statutory schemes
- create a statutory scheme
- configure statutory program eligibility
- add statutory contribution types
- enroll an employee in a statutory scheme
- view statutory schemes in Compliance and Taxation
- explain why statutory schemes are read only
- explain why statutory schemes are unavailable

### Retrieval tags
- payroll
- statutory-schemes
- statutory-programs
- contribution-types
- compliance
- enrollment
- direct-answer

### Answer objective
Explain scheme setup, employee enrollment, permissions, and Payroll dependency.

### Instructions
- Answer directly without calling executable tools.
- Do not provide legal or jurisdiction-specific statutory advice.
- For setup or assignment changes, explain the effect and ask for confirmation before a data-changing action is executed.

### Direct answer
Payroll admins manage statutory scheme setup in [Payroll -> Statutory Schemes]({{payroll_statutory_url}}) where the statutory module is available. A statutory scheme can include scheme details, contribution types, statutory programs, eligibility rules, calculation bases, output lines, and eligible employees.

To create a scheme, complete the three steps in the form: **Details**, **Contribution Types**, and **Eligible Employees**. Choose the Work Location and currency in Details, define each employee or employer contribution and its calculation method, then review eligibility and assignments. Formula contribution types must use valid available variables and must not divide by zero.

The pay run must also be configured to apply statutory contributions. During calculation, eligibility, effective dates, Work Location, employee data, and scheme assignments determine whether a contribution appears. Review employee and employer contribution sections separately: an employer contribution can appear in Payroll results without increasing the employee's net pay deduction.

For an individual employee, open the employee profile and select **Compliance & Taxation**. When Payroll is installed and schemes are available for that employee, the statutory-scheme section appears there.

Authorized admins can add or remove enrollments. Other permitted users may see assigned schemes as read-only labels. If editing or deleting is blocked, review whether employees or pay runs depend on the scheme before changing it. Availability depends on the employee, Work Location, Payroll installation, scheme eligibility, and access permissions.
