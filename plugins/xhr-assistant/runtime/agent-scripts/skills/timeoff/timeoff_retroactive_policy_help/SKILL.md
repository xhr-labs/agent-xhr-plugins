---
name: timeoff-retroactive-policy-help
description: Explain Time Off retroactive policy recalculation. Use when the user asks about applying policy changes retroactively, recalculating balances, or accrual reset behavior.
---

# Time Off Retroactive Policy Help

## Intent: timeoff-retroactive-policy-help
### User request patterns
- apply time off policy retroactively
- recalculate leave balances
- explain retroactive accrual reset
- update a policy for past periods
- recalculate time off policy balances

### Retrieval tags
- timeoff
- retroactive
- recalculation
- accrual
- direct-answer

### Answer objective
Explain retroactive recalculation and caution users about balance impact.

### Instructions
- Answer directly without calling executable tools.

### Direct answer
Open [Time Off Configuration]({{timeoff_configuration_url}}) and select the relevant policy.

Retroactive recalculation applies a policy from an earlier date in the current calendar year and rebuilds the generated accrual result for the affected period. It can change employee balances.

By default, the recalculation preserves manual balance corrections, approved-leave history, and carry-over. Separate reset choices can reverse manual corrections or remove previously generated policy accruals and opening balances before rebuilding them. Those reset choices should be used only when the existing setup is known to be wrong.

Before applying it, confirm the policy, affected employees, effective date, allowance, eligibility, and expected balance impact. A future date or a date outside the current calendar year is not valid for this setup flow.
