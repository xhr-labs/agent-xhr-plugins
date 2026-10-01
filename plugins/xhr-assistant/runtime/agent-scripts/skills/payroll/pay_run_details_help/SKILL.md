---
name: payroll-pay-run-details-help
description: Explain Payroll pay run details. Use when the user asks about pay run results, net pay, earnings, deductions, statutory contributions, tax, manual adjustments, or approval details.
---

# Pay Run Details Help

## Intent: payroll-pay-run-details-help
### User request patterns
- view pay run details
- explain net pay in a pay run
- review earnings and deductions
- show statutory contributions in payroll
- explain payroll approval details

### Retrieval tags
- payroll
- pay-run
- net-pay
- earnings
- deductions
- direct-answer

### Answer objective
Explain the business tabs and review purpose of the pay run detail view.

### Instructions
- Answer directly without calling executable tools.
- Keep employee payroll data private. Describe only records the user is authorized to view.
- If the user wants to approve, publish, void, import, or change a pay run, explain the effect and ask for confirmation before an action skill executes it.

### Direct answer
Open [Payroll -> Pay Runs]({{pay_runs_url}}) and select the pay run.

The pay run detail view helps payroll teams review payroll results before approval or completion. Results are organized into business tabs such as **Net Pay**, **Earnings**, **Deductions**, **Statutory contributions**, and **Tax**.

Use **Net Pay** to compare the final payable amount with gross pay and deductions. Use **Earnings** and **Deductions** to check each pay component. Use **Statutory contributions** to review employee and employer contributions separately. Use **Tax** to review the applied tax scheme, taxable values, reliefs, and tax result when tax is enabled.

Where supported, payroll admins can filter results by department, inspect calculation details, review manual or custom formula inputs, and preview a temporary payslip while the run is **Calculated**. Draft amounts can show formulas or input placeholders; calculated, approved, and published runs show numeric results.

Before approving, check the employee list, work location, pay period, gross and net totals, deductions, tax, statutory contributions, negative-net-pay warnings, and any calculation errors. If something is wrong, return the run to draft where the current status allows it, correct the source data or setup, and recalculate. Do not edit unrelated components to force a total to match an expectation.

The usual review sequence is **Draft -> Calculating -> Calculated -> Approved -> Published**. An **Error** run can be corrected and calculated again. A **Calculating** run may take time because calculation is asynchronous; wait for it to reach **Calculated** or **Error** before reviewing results or trying another lifecycle action. A **Void** run is not an active run.
