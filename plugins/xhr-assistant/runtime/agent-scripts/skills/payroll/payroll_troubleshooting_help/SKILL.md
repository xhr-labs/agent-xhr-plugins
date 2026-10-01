---
name: payroll-troubleshooting-help
description: Troubleshoot Payroll setup, permissions, calculation failures, unexpected results, formula errors, proration, tax, statutory contributions, payslips, and compliance exports.
---

# Payroll Troubleshooting Help

## Intent: payroll-troubleshooting-help
### User request patterns
- troubleshoot the first Payroll run
- explain why a pay run cannot be calculated
- fix a pay run stuck in calculating
- explain why an employee is missing from a pay run
- explain a Payroll calculation error
- fix a pay component formula error
- explain why tax is missing from a pay run
- explain why statutory contributions are missing
- explain why a payslip is not available
- troubleshoot a WPS or SIF export
- explain why a pay component cannot be deleted
- explain why a tax or statutory scheme cannot be deleted
- check why Payroll setup is incomplete

### Retrieval tags
- payroll
- troubleshooting
- pay-run
- permissions
- formula
- proration
- tax
- statutory
- payslip
- compliance-export
- edge-cases
- direct-answer

### Answer objective
Give a practical, user-facing diagnosis for Payroll problems. Start with the smallest likely cause, name the screen and setting to check, explain what the current run state allows, and hand off sensitive or jurisdiction-specific decisions to the payroll owner.

Start from [Payroll -> Pay Runs]({{pay_runs_url}}) when the issue concerns a run, calculation, result, export, or payslip.

### Instructions
- Answer directly without calling executable tools.
- Do not expose API paths, service names, database details, internal error classes, tokens, or implementation identifiers.
- Do not claim that a feature is available just because it appears in a proposal or technical document. Retro Pay is not a current Payroll workflow.
- Treat every action that changes pay components, structures, schemes, employee assignments, pay runs, manual inputs, or exports as a user-controlled action. Explain the action and ask for confirmation before a separate action skill executes it.
- Never reveal private payroll amounts or payslip data for an employee other than the authenticated user unless the product view and the user's permission explicitly support that access.
- If the user asks for legal, tax, or statutory advice, explain the configured product behavior and recommend confirmation with the local payroll or compliance owner.

### Triage order

1. Check access first.
   - The Payroll app has separate view and edit permissions for Pay Components, Pay Structures, Payroll Runs, Statutory, Tax Schemes, Configurations, and App Permissions.
   - A user may be able to view or export information without being allowed to edit it. Creating, changing, deleting, assigning, importing, calculating, approving, publishing, or voiding requires the relevant edit permission.
   - If a page is forbidden or an action is missing, open Payroll -> App Permissions or ask an app administrator to check the relevant data block. Do not infer that a platform Admin automatically has every Payroll app permission.
   - If permissions were just changed, refresh the app and reopen the Payroll page. If the permission still does not appear, the app administrator should verify both app access and the data-block permission.

2. Check the setup dependencies.
   - Create at least one Pay Component before creating a Pay Structure.
   - Pay Components and Pay Structures are tied to a Work Location. A component or structure from another location is not a substitute.
   - A pay run needs a Work Location, a valid pay period, a Pay Structure for that location and tax setting, and at least one employee assigned to the same location.
   - If the Pay Run wizard says no structure is available, first check that a structure exists for the selected location and that its tax setting matches the wizard's tax setting. If no components exist, create those first.
   - If employees do not populate, confirm that they belong to the selected Work Location. The wizard initially finds employees for the selected location, but the user can adjust the assignment before saving.

3. Check employee source data.
   - Confirm the employee is active and assigned to the expected Work Location.
   - Confirm the employee has the compensation, payment, and employment information required by the configured components and local payroll process.
   - A formula, tax rule, statutory rule, or manual input may require a value that is absent for one employee. Review that employee's result detail and the source data rather than changing the formula blindly.
   - If only one employee is wrong, compare that employee's effective dates and source values with an employee who calculated successfully.

4. Check the pay run state before trying another action.
   - DRAFT: review or edit setup, add or remove employees, enter manual or custom formula inputs, then calculate.
   - CALCULATING: wait for the calculation to finish. The result may not be ready immediately. Refreshing the page resumes status checking. Do not start duplicate calculations while this state is active.
   - CALCULATED: review result tabs and employee details, preview a payslip if available, then approve or return the run to draft for correction.
   - ERROR: review the displayed error details, correct the source configuration or inputs, and calculate again.
   - APPROVED: publish payslips when the pay date is correct. Do not expect draft editing here.
   - PUBLISHED: the run has been published and employee self-service payslips can become available. Treat it as a historical payroll result when investigating corrections.
   - VOID: the run is no longer an active payroll run. Start or correct a separate run according to the payroll owner's process.

5. Diagnose formulas and custom inputs.
   - Use only variables offered for the selected Work Location. A variable from another location or an invented variable will not resolve.
   - Unknown variables, invalid syntax, incompatible value types, circular component references, division by zero, and negative results can prevent a pay component formula from being saved or calculated.
   - Check the formula in small pieces. Confirm each referenced pay component exists, belongs to the same location, and is not referring back to the component being edited.
   - Custom formula inputs are entered per pay run in the draft input matrix. Empty cells are not automatically the same as a meaningful zero. Check the default value and the employee-specific value before calculating.
   - If the app asks for acknowledgement of custom formula inputs, review the input matrix and acknowledge it before calculating. Do not acknowledge values that have not been reviewed.
   - If a formula is valid but one employee still fails, inspect that employee's input value and source data. A formula can be structurally valid while a resolved value is missing or invalid for a particular employee.

6. Diagnose proration and period differences.
   - Proration can change a full-period amount when an employee or component is effective for only part of the period, or when the configured rule uses working days or calendar days.
   - Check the Work Location's default proration rule and any period standard-days override in Payroll -> Configurations.
   - A dynamic standard-days rule can use a period override. A fixed standard-days rule uses its configured fixed denominator instead.
   - In a draft pay run, a formula component may have a component-specific evaluation period. This changes the formula input period for that component; it does not change the pay run period, tax period, statutory period, reporting period, or approval flow.
   - Fixed and legacy manual-input components do not use the same formula proration controls as formula components. Do not promise proration behavior without checking the component method.
   - Use the proration summary and audit details to compare the period, effective dates, leave segments, rule, numerator, denominator, and resulting amount. If the result is still disputed, send that evidence to the payroll owner.

7. Diagnose tax.
   - Tax is calculated only when the pay run and its Pay Structure are configured to apply tax, and the relevant tax setup is available for the Work Location and employee.
   - Check the selected tax setting on both the pay run and Pay Structure before changing a tax scheme.
   - Check the tax scheme's effective dates, base (taxable income or gross income), bracket strategy, continuous brackets, relief rules, eligibility criteria, and explicit employee exclusions.
   - A scheme can be valid for one employee and not another because eligibility is evaluated against employee data and effective dates. Review the employee's eligibility result instead of assuming a missing tax line is a calculation bug.
   - If tax details are absent, explain whether tax was disabled, no eligible scheme applied, or the calculation produced an error. Do not make a legal conclusion about whether tax should apply.

8. Diagnose statutory contributions.
   - Check that the pay run is configured to apply statutory contributions.
   - Check the scheme's Work Location, contribution types, calculation method, eligibility rules, effective dates, and employee assignment or eligibility.
   - Review employee and employer contribution sections separately. An employer contribution may be present in Payroll results without being part of the employee's payslip amount.
   - Formula contribution types can fail for the same reasons as pay component formulas, including missing variables, invalid arithmetic, and division by zero.
   - Do not tell the user which contribution or rate is legally required. Confirm the configured result with the local payroll or compliance owner.

9. Diagnose exports and payslips.
   - CSV export is available for non-draft pay runs. If it is missing, check the run state and view permission.
   - UAE WPS/SIF export is available only for UAE runs in a calculated, approved, or published state. Review the preview, mappings, employer details, employee details, and selected rows.
   - Structural export failures block the download. Soft validation warnings may allow an explicit export-after-warning choice, but the payroll owner must decide whether to proceed.
   - A calculated run may offer a temporary payslip preview for review. Official employee payslip access follows the publication and self-service flow; a preview is not the same as a published payslip.
   - Employees use My Profile -> Compensation -> My Earnings for their own pay history and payslips. If a published payslip is still processing, retry the download after the request completes. Do not suggest another employee's payslip URL or data.

10. Diagnose blocked edits or deletes.
   - A missing Edit or Delete action can mean the user has view permission only, the resource has dependencies, or the current run state does not allow the change.
   - A Pay Component may be referenced by formulas, Pay Structures, or draft pay runs. A Pay Structure may be referenced by pay runs. Review the dependency warning before deleting.
   - A Statutory Scheme may be assigned to employees or referenced by pay runs. A Tax Scheme may be assigned, used by an active run, or retained in payroll history. The product may block deletion or offer archive behavior to protect history.
   - A resource involved in a calculation may be temporarily locked. Wait for CALCULATING to finish and retry only after reviewing the updated dependency state.
   - Never recommend deleting a historical configuration to correct a published payroll. Use the supported correction process owned by payroll.

### Common answer shape

When the user gives a Payroll error, answer in this order:

1. State the most likely cause in plain language.
2. Give the exact Payroll screen and setting to check.
3. Explain what the current pay run state permits.
4. Give one safe correction path and one reason not to change unrelated settings.
5. Ask for the visible status or error text if the diagnosis depends on it.

### Safe escalation

- Ask for the pay run status, Work Location, affected employee count, and visible error text. Do not ask for salary amounts, bank details, access tokens, or full payslips in chat.
- Escalate to the payroll owner when the issue concerns legal treatment, statutory rates, tax interpretation, published payroll corrections, or an export that may be submitted to a regulator or bank.
