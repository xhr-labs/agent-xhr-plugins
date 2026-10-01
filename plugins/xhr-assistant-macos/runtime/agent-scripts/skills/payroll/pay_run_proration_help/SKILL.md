---
name: payroll-pay-run-proration-help
description: Explain Payroll pay run proration. Use when the user asks about prorated pay, proration audit, calculation summaries, partial periods, or why a pay run amount changed.
---

# Pay Run Proration Help

## Intent: payroll-pay-run-proration-help
### User request patterns
- explain prorated pay
- review pay run proration
- why did payroll prorate this amount
- view proration audit
- explain partial period payroll calculation

### Retrieval tags
- payroll
- proration
- audit
- pay-run
- direct-answer

### Answer objective
Explain how proration visibility helps payroll review calculations.

### Instructions
- Answer directly without calling executable tools.
- Do not invent a proration result from the final amount alone. Use the visible audit values and the configured rule.
- If the user wants to change a rule, override, or pay run, ask for confirmation before a data-changing action is executed.

### Direct answer
Open [Payroll -> Pay Runs]({{pay_runs_url}}) and select the pay run to review proration details.

Pay run proration helps payroll teams understand adjustments for partial periods, employee changes, effective dates, leave segments, or other rules that affect the calculated amount. The proration audit and summary views are intended to make calculation adjustments easier to review.

Use proration details when a result looks different from the expected full-period amount. Check the component method first: formula components can use the formula proration controls, while fixed and legacy manual-input components do not use the same formula proration behavior.

For a location-scoped rule, review **Payroll -> Configurations**. A rule uses either working days or calendar days and can use dynamic standard days or a fixed standard-day value. A period standard-days override affects the denominator only when the rule uses dynamic standard days. It does not change the pay run period.

In a draft run, a formula component can have its own evaluation period. This changes the input period for that component only; it does not change the pay run period, tax period, statutory period, reporting period, or approval flow. Use the audit to compare the selected period, effective dates, rule, numerator, denominator, and resulting amount.

If the audit does not explain the difference, compare the affected employee's effective dates and source values with a successful employee, then escalate the evidence to the payroll owner. The exact calculation still depends on payroll setup, employee data, effective dates, pay components, and configured payroll rules.
