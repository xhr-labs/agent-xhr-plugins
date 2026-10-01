---
name: final-settlement-setup-help
description: Explain how to set up Final Settlement / EOS in X-HR. Use when the user asks how to setup EOS, end-of-service settlement, final settlement setup, settlement items, EOSG schemes, or Offboarding settlement configuration.
---

# Final Settlement Setup Help

## Intent: final-settlement-setup-help
### User request patterns
- How to setup EOS
- how do I set up end of service
- setup EOS gratuity
- configure final settlement
- set up settlement items
- set up EOSG schemes
- configure offboarding settlement
- prepare Final Settlement setup

### Retrieval tags
- final-settlement
- eos
- end-of-service
- eosg
- gratuity
- offboarding
- settlement-setup
- settlement-items
- payroll-handoff
- direct-answer

### Answer objective
Give HR/Admin users a concise setup runbook for Final Settlement / EOS without executing tools or implying unsupported workflow depth.

### Instructions
- Answer directly without calling executable tools.
- Treat "EOS" as end-of-service / final settlement setup unless the user is asking for an amount estimate; amount estimates belong to `skills/payroll/get_my_end_of_service_estimate/SKILL.md`.
- Keep the answer implementation-accurate: Final Settlement / Offboarding setup centers on settlement items, EOSG schemes, settlement records, permissions, and payroll handoff readiness.
- Be cautious where product contracts may vary by tenant or rollout. Do not claim that every workflow is enabled for every tenant.
- If the user asks for a step-by-step setup, include the setup order below.
- If the user asks where to configure it, mention the Final Settlement / Offboarding app setup areas: Settlement Items and EOSG Schemes.
- If the user asks why an estimate or settlement is wrong, direct them to review employee termination data, joining date, salary basis, unpaid leave, configured settlement items, active EOSG scheme, and payroll handoff configuration.
- Do not provide legal advice or statutory interpretation beyond configured product behavior.

### Direct answer
To set up EOS / Final Settlement, first make sure the Final Settlement or Offboarding app is enabled for the tenant and that the right HR or payroll users have access.

Then configure the setup areas in this order:

1. **Settlement Items**
   - Open the Final Settlement / Offboarding setup area for Settlement Items.
   - Set up the earning, deduction, and statutory items that can appear on settlement records.
   - Use the initial setup screen or templates where available.
   - Select the relevant work location because settlement item definitions and auto-populate behavior are location-scoped.
   - Keep required items selected, and enable auto-populate only for supported item types such as EOSG statutory items or supported formula-based items.

2. **EOSG Schemes**
   - Open the EOSG Schemes setup area.
   - Create or review the scheme for the relevant work location.
   - Configure the scheme overview, effective period, eligibility rules, and calculation rules.
   - Calculation rules can include basis formula, eligible-days formula, entitlement-rate breakpoints, and a maximum cap where supported.
   - Activate the draft scheme before preparing settlements that should use it.

3. **Settlement Records Workflow**
   - Settlement records are used to review an employee's final settlement after an exit or termination event.
   - A draft settlement can be prepared from employee, last-working-day, and termination-reason inputs.
   - Draft settlements can be reviewed, adjusted where allowed, and submitted for approval.
   - Approved settlements should become locked in Offboarding and then move to Payroll handoff where enabled.

4. **Payroll Handoff Readiness**
   - Confirm how approved settlement lines map into Payroll for off-cycle payout.
   - Check that pay components, pay structures, statutory setup, and work-location payroll setup are ready before expecting payout execution.
   - Payroll remains the payout execution surface; Final Settlement tracks review, approval, and handoff.

5. **Permissions**
   - Check app access and data-block permissions for HR, payroll, approvers, and viewers.
   - Users without access may not see the app or may be blocked from setup, approval, or handoff actions.

If the setup is incomplete, start by checking whether Settlement Items exist for the work location, whether an active EOSG scheme exists for that location and effective date, whether the employee's termination and employment data are correct, and whether Payroll handoff configuration is available.
