---
name: exm-expense-policies-help
description: Explain expense policies - rule types, severities, periods, eligibility, priority and lifecycle, conflicts, and the limits on editing a policy that already has results - without calling tools.
---

# Expense Policies (How-to)

## Intent: exm-expense-policies-help
### User request patterns
- what are expense policies
- how do spending limits work in expense management
- what is the difference between hard block and soft warning
- how do I set a per-day meal limit
- what does the priority on an expense policy do
- why can I not edit the rules of this policy
- what is a policy conflict
- who does an expense policy apply to

### Retrieval tags
- exm
- expense-management
- expense-policies
- spending-limits
- policy-rules
- policy-lifecycle
- direct-answer

### Answer objective
Explain how the expense policy engine is structured and which constraints govern creating, editing, and retiring a policy.

### Instructions
- Answer directly without calling executable tools.
- Do not claim a policy exists or was changed; use `skills/exm/list_expense_policies` and `skills/exm/manage_expense_policy` for live data and changes.
- Expense policies are not enabled in every environment. If the user cannot see the Policies screen, say the feature is not available to them there rather than insisting on the menu path.

### Direct answer
Expense policies check an expense as it is submitted. They live under Configuration in [Policies]({{expenses_policies_url}}) and are guarded by their own permission datablock.

A policy is built in four steps: **Details** (name, description, enabled switch, priority, effective from and to), **Eligibility** (who it applies to), **Rules**, and a **Summary** review. Leaving eligibility empty applies the policy to every employee in the company; conditions can be combined as match all, match any, or match none. Priority orders evaluation when several policies apply, and effective dates can be open ended.

Each rule has a **rule type**, a **severity**, and a **period**. Rule types cover category access, amount limits, required receipt, description, client, project, attendees or merchant, submission windows, blocked future dates, merchant, payment method and flight cabin restrictions, mileage rate, per-night and per-attendee limits. Severity decides the consequence: **hard block** stops the submission, **soft warning** lets it through with a warning attached to the expense, and **info** is advisory. The period sets what the limit is measured over - per expense, day, week, month, quarter, year, trip, night, attendee, or distance unit. A rule can be scoped to one category or apply to all of them.

Two states are independent: the policy **status** (draft, scheduled, active, archived) and the **enabled** switch. An active policy that is switched off is not evaluated.

Saving is checked for overlaps: when a new or edited policy conflicts with an existing one, the app reports the overlapping policy and can suggest an action or an earlier end date before you save. Once submitted expenses reference a policy, its rules are locked and it cannot be hard deleted - only metadata, the enabled switch, and safe dates can change. Archive it and create a replacement for future changes; archived policies are ignored during evaluation but kept for history.
