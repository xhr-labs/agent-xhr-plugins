---
name: payroll-formula-help
description: Explain Payroll formula behavior, calculation methods, available variables, formula authoring, custom formula inputs, proration, statutory calculation formulas, and formula troubleshooting.
---

# Payroll Formula Help

## Intent: payroll-formula-help
### User request patterns
- explain how Payroll formulas work
- choose a Payroll calculation method
- create a formula pay component
- calculate a percentage contribution
- find variables for a Payroll formula
- explain which formulas Payroll supports
- use salary or compensation in a formula
- use overtime or attendance in a formula
- use leave days in a formula
- use employee information in a formula
- use a custom formula input
- explain why a formula is invalid
- explain why a formula result is different
- troubleshoot a formula calculation error
- explain formula proration

### Retrieval tags
- payroll
- formula
- calculation-method
- pay-components
- statutory
- variables
- custom-inputs
- attendance
- timeoff
- proration
- troubleshooting
- direct-answer

### Answer objective
Explain Payroll formulas in plain language and help the user choose a supported setup. Use the current formula suggestions for the selected Work Location as the source of truth. Distinguish pay component formulas, statutory contribution calculations, proration rules, and run-specific custom inputs.

Open [Payroll -> Pay Runs]({{pay_runs_url}}) when the question concerns formula results, custom inputs, calculation, or a pay-run error. For formula authoring, direct the user to the Pay Components or Statutory Scheme form inside Payroll.

### Instructions
- Answer directly without calling executable tools.
- Do not expose raw component IDs, variable IDs, API paths, service names, database details, or internal error codes. Tell users to select the visible variable or chip from the Formula field so Payroll inserts the correct reference.
- Treat formula creation, component changes, statutory changes, custom input changes, and pay-run calculation as user-controlled actions. Explain the impact and ask for confirmation before a separate action skill executes a change.
- Never invent a variable, formula field, calculation method, function, currency conversion, or legal rule. If a variable is not offered for the selected Work Location, explain the likely prerequisite and ask the user to choose an available variable.
- Keep pay, tax, statutory, attendance, and employee information private. Do not request salary amounts, bank details, full payslips, or access tokens in chat.
- Do not provide legal, tax, or statutory advice. Explain configured product behavior and direct jurisdiction-specific questions to the payroll or compliance owner.

### Calculation methods

#### Pay Components

The Pay Component form currently offers these authoring choices:

- **Fixed Amount**: a non-negative default amount and the Work Location currency. The component starts from that configured amount before any applicable payroll period handling.
- **Formula**: a numeric expression built from constants, arithmetic operators, parentheses, and variables selected for the component's Work Location. The result is calculated separately for each employee and pay period.

Do not offer **Percentage** as a Pay Component method. The backend enum contains that value for compatibility, but current Pay Component creation and update reject it. If the user wants a percentage-based earning or deduction, guide them to a Formula Pay Component that multiplies a selected numeric base by a rate, then validate the formula in the form.

Pay Components can be **Earnings** or **Deductions**. A deduction formula should normally return a positive amount; the component type determines that it is deducted from net pay. Do not force a formula to become negative to represent a deduction. Pay component formula results that are negative are rejected by current validation.

#### Statutory contribution calculations

Statutory contribution types have a different set of choices:

- **Fixed Amount**: a fixed value in the scheme currency.
- **Percentage**: a percentage of the configured calculation base. The current calculation applies the percentage to the base and rounds the resulting contribution to two decimal places.
- **Formula**: a numeric expression using the formula variables available for the scheme's Work Location.

The statutory form can also define a **Calculation Base** formula and optional base limits. Contribution amount limits can be fixed values or formulas. The contribution amount can be defined separately for the employee and employer payer. A percentage contribution requires an enabled, non-empty calculation base; otherwise the percentage option is unavailable in the form.

Do not confuse a statutory percentage choice with a Pay Component percentage method. They are different product flows.

#### Tax schemes

The current Tax Scheme form uses a tax base, flat-rate or progressive brackets, relief rules, eligibility criteria, and exclusions. It is not a free-form Pay Component formula editor. Explain tax calculations through those configured fields, not by inventing a tax formula.

### Common calculation patterns

Map the user's goal to the simplest supported Payroll setup:

- **Fixed recurring amount**: use Fixed Amount when the same amount applies to everyone in the component's Work Location.
- **Percentage of another amount**: use a Formula Pay Component such as `Basic Salary * 0.10`, or use the Statutory Contribution Percentage option when the contribution belongs to a statutory scheme.
- **Hourly or daily amount**: multiply an approved hour/day variable by a configured rate, for example `Approved Overtime Hours * Overtime Rate`. Confirm whether the source is Attendance data or a custom run input.
- **Leave-related deduction**: use the relevant leave-day variable and the agreed daily rate, for example `Unpaid Leave Days * Daily Rate`. Confirm the leave type and pay-period dates first.
- **Employee-specific one-off amount**: use a Formula component with a Custom Input when the value is only known during the pay run.
- **Prorated joiner, leaver, or partial-period amount**: use a Formula Pay Component with the configured proration rule, then verify the effective dates, paid days, and standard-day setting.
- **Employer or employee statutory contribution**: configure the payer-specific amount in the Statutory Scheme. Use Percentage for a base percentage, Formula for a more specific numeric rule, and the scheme's base or amount limits for caps and floors.
- **Progressive or relief-based tax**: configure tax brackets, tax base, reliefs, eligibility, and exclusions in the Tax Scheme. Do not replace this with a Pay Component formula.

If the requirement depends on a text value, date comparison, conditional branch, currency conversion, a legal threshold, or a country-specific rule, do not invent a formula. Check whether the active form has a dedicated field or limit for it and escalate jurisdiction-specific behavior to the payroll or compliance owner.

### Formula syntax currently safe to author

In the normal Payroll forms, guide users to build formulas with:

- numeric literals such as `0`, `100`, or `0.15`
- variables selected from the Formula field suggestions
- `+`, `-`, `*`, and `/`
- parentheses to make the intended order clear

Conceptual examples should use visible names, not raw identifiers:

- Housing allowance: `Basic Salary * 0.15`
- Hourly overtime: `Approved Work Hours * Hourly Rate`
- Attendance bonus: `Approved On-Site Working Days * Daily Bonus`
- A deduction based on earnings: `Basic Salary * 0.05`
- A statutory base: `Basic Salary + Housing Allowance`

In the actual form, the user selects each visible variable and Payroll stores the corresponding reference. Do not ask the user to type a component identifier. If the same name appears more than once, ask which Work Location or visible component they mean.

The runtime formula engine recognizes `IF`, `MIN`, and `MAX`, but the current frontend formula validator authorizes only arithmetic symbols, parentheses, numbers, and selected variables for normal authoring. Therefore do not promise that a newly typed function call will save through the current Payroll form. Prefer an arithmetic formula and the dedicated statutory limits fields. Treat function expressions as compatibility behavior unless the active UI accepts them.

### Variable families

The formula suggestions are filtered by the selected Work Location. The exact list can change when payroll data, Attendance, Time Off, Compensation and Benefits, or other source configuration changes. Explain the families like this:

- **Pay Components**: existing components in the same Work Location. A component can reference a fixed amount or another formula component. Referenced components are evaluated before the component that uses them.
- **Calendar**: the approved working-day count for the pay period. This is useful for daily rates and working-day comparisons.
- **Compensation**: active Compensation and Benefits component values for the employee and selected Work Location, such as a salary or other configured compensation type. These values are money values and must use the expected currency.
- **Employee profile**: visible employee attributes such as Job Title, Employment Type, Work Location, Department, Team, Birth Date, Gender, Marital Status, Nationality, and Hire Date. Use numeric or money variables for arithmetic; do not use text, date, country, or enum-like values as if they were amounts.
- **Attendance**: approved work hours, approved overtime hours by overtime category, and approved on-site or remote working days. Only recommend these when Attendance data is actually used and approved for the pay period. If the company does not use attendance or roster-based time tracking, do not add Attendance variables just because they exist in the catalog.
- **Time Off**: unpaid leave, leave days for configured leave types, and relevant maternity leave values when those source facts are available. If a leave type is not configured, its variable will not be available.
- **Employment**: hire and termination dates, termination reason, active-at-period-end, terminated-in-period, service days, service years, unpaid leave days, and eligible service days or years. These values are period-aware and may differ between pay runs.
- **Termination settlement**: an approved termination settlement amount when the employee has one. Do not assume a settlement exists for every employee.
- **Custom input**: a run-specific numeric value entered per employee in the draft pay run. It is useful when a value is known only at payroll-run time and should not be stored as a reusable employee or compensation field.

The catalog can contain variables used for eligibility or specialized runtime scenarios that are not suitable for arithmetic amount formulas. Use the variable's visible data type and the current Formula field suggestions as the authority.

### How a formula is evaluated

Explain the lifecycle without exposing implementation details:

1. The user selects a Work Location and Payroll loads the variables valid for that location.
2. The user chooses Formula and selects visible variables or enters numeric constants and operators.
3. The frontend checks the expression shape, selected variables, and obvious division-by-zero cases. The Payroll service validates it again before saving or calculating.
4. During a pay run, Payroll resolves each variable for the employee and the relevant period. Pay Component references are evaluated in dependency order, so a formula can use the result of another component.
5. Payroll stores calculation evidence for review, including the formula and resolved inputs where the result view supports it. A calculated run uses the values captured for that calculation; changing live setup later does not rewrite an already calculated historical result.
6. Tax, statutory contributions, proration, net pay, and payslip output use the calculated component results according to their own configuration. Do not recompute a final payslip amount from the displayed formula text alone.

### Custom formula inputs

Custom inputs are not a fourth Pay Component calculation method. They are named numeric operands inside a Formula component and are filled in for a particular draft pay run.

- New custom keys must start with a lowercase letter and may contain lowercase letters, numbers, and underscores, up to 64 characters. Use a meaningful name such as `overtime_hours` or `sales_bonus`, not a salary amount embedded in the key.
- When authoring is enabled, typing a valid custom key in the Formula field offers an Add custom variable suggestion. Selecting it creates a custom variable chip.
- The draft pay run shows a matrix of employees and custom variables. Enter non-negative decimal values per employee. Blank cells remain empty while editing.
- Save only the cells that should be explicit. A shared default can be saved when the same reviewed value should apply to multiple employees; tell the user to verify the affected employees before saving it.
- Before calculation, review defaulted cells and acknowledge them when the dialog asks. After acknowledgement, blank/defaulted cells resolve as zero for that calculation. Do not describe an empty draft cell as already being a confirmed zero.
- Custom input values and formulas are frozen for the calculation attempt so the result can be explained later. If a value changes, update the draft and calculate again.
- If the custom-input matrix cannot load, retry the matrix before calculating. Do not bypass the acknowledgement step.

### Proration and formulas

- Formula Pay Components can use proration controls. Selecting Formula in the current Pay Component form enables proration by default, but the user can review the setting.
- Fixed Amount components do not use the same formula proration controls.
- A Work Location supplies the default proration rule. The rule can use working days or calendar days and dynamic or fixed standard days. A period override changes the denominator only for a dynamic-standard-days rule.
- A draft pay run can set an evaluation period for a formula component. This changes the period used to resolve that component's formula inputs; it does not change the pay run, tax, statutory, reporting, or approval period.
- If a formula result looks low or high, inspect effective dates, leave segments, the selected rule, paid days, standard days, and the formula's resolved inputs before changing the formula.

### Validation and troubleshooting

Explain failures using the visible error and these causes:

- **Formula required**: Formula was selected but the expression is empty.
- **Invalid syntax**: Use numbers, parentheses, arithmetic operators, and variables inserted from the current suggestions. Remove unsupported words or symbols.
- **Unknown variable**: The variable is not available for the selected Work Location, was typed incorrectly, or its source configuration is missing. Re-select it from the suggestions.
- **Division by zero**: The formula divides by a literal zero or resolves a denominator to zero. Add a valid denominator or use a dedicated configuration field that supports limits; do not hide the issue with an arbitrary constant.
- **Circular reference**: Component A refers to B while B refers back to A, directly or through other components. Break the cycle and keep the dependency chain one-way.
- **Type or currency mismatch**: Use numeric or money variables of the expected Work Location currency in amount formulas. Do not combine amounts from different currencies or use text/date/profile values as money.
- **Negative result**: Pay Component formulas must produce a non-negative result for current validation. For a deduction, keep the formula amount positive and use the DEDUCTION component type.
- **Valid formula but one employee fails**: Check that employee's source compensation, effective dates, attendance or leave data, custom input, and eligibility. A formula can be valid for the structure but unresolved for one employee.
- **Formula shows in draft instead of an amount**: This is expected before calculation. Draft rows can show the formula or input placeholder; calculated rows show the resolved numeric amount.
- **Formula changed but result did not**: Check the pay run state. A calculated or later run uses its captured calculation values. Return an eligible run to draft or create a new run according to the payroll owner's correction process.

### Safe answer pattern

When a user asks for a formula, answer in this order:

1. Confirm whether they are configuring a Pay Component, statutory contribution, proration rule, or run-specific custom input.
2. State the supported calculation choice for that screen.
3. Ask for or use the Work Location and the visible variable names; never invent hidden references.
4. Give the plain-language formula and explain whether the result is an earning, deduction, employer contribution, or employee contribution.
5. Mention proration, tax treatment, currency, or custom-input review only when relevant.
6. Ask the user to preview the formula result and confirm before saving or calculating.
