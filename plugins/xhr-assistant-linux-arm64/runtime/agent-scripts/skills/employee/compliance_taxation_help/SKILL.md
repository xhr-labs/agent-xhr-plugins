---
name: employee-compliance-taxation-help
description: Explain the employee Compliance and Taxation profile area in X-HR. Use when the user asks about tax residency, tax identifiers, country-specific compliance fields, effective-dated profiles, payroll tax schemes, or UAE-specific profile behavior.
---

# Compliance and Taxation Help

## Intent: employee-compliance-taxation-help
### User request patterns
- update an employee tax profile
- manage employee compliance data
- set employee tax residency status
- view country specific compliance fields
- manage payroll tax or statutory scheme assignments

### Retrieval tags
- employee
- compliance
- taxation
- tax-residency
- direct-answer

### Answer objective
Explain the location-aware compliance profile and effective-date behavior.

### Instructions
- Answer directly without calling executable tools.
- Avoid giving legal or tax advice; describe product behavior only.

### Direct answer
Open [People]({{people_url}}), select the employee profile, and open **Compliance & Taxation**.

The fields shown are resolved from the employee's work-location country and may include tax identification, residency status, localized compliance attributes, dependents, statutory schemes, and payroll tax-scheme assignment. Authorized users can edit the active effective-dated profile, review historical or scheduled profiles, and create a future profile where supported.

Country behavior varies. For example, UAE profiles use localized compliance fields and hide profile areas that do not apply. Payroll may warn or block changes when the compliance data is already used by a protected pay run.
