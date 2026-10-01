---
name: timeoff-carryover-help
description: Explain Time Off carry-over configuration, limits, expiry, FIFO consumption, forfeiture, and advance-leave debt. Use when the user asks about unused leave moving into a later period.
---

# Time Off Carryover Help

## Intent: timeoff-carryover-help
### User request patterns
- configure leave carry-over
- carry unused leave to next year
- explain time off carry-over
- set carry-over limits
- update carry-over in a time off policy

### Retrieval tags
- timeoff
- carry-over
- policy
- leave-balance
- direct-answer

### Answer objective
Explain carry-over as part of time-off policy setup.

### Instructions
- Answer directly without calling executable tools unless the user asks Lumi to generate a policy setup.

### Direct answer
Open [Time Off Configuration]({{timeoff_configuration_url}}) and select the relevant policy.

Carry-over controls whether unused positive leave can move into the next accrual cycle. In the policy, you can choose whether it is enabled, set a maximum number of days, and optionally set an expiry period.

At the end of the cycle, the system carries forward the allowed amount and forfeits any excess. When leave is approved, carry-over is used before regular accrued leave. Expired carry-over is removed from the available balance.

If advance leave is enabled and an employee finishes a cycle with a negative balance, that debt can continue into the next cycle. It is separate from positive carry-over and is paid down by future accruals.

If an employee's request crosses dates with different advance-leave rules, split it into separate requests. Carry-over does not require manual setup for each employee; it is applied by the policy at the cycle boundary.
