---
name: helpdesk-subscription-upgrade-help
description: Explain X-HR subscription plans, company-effective pricing, billing cycles, payment-card setup, upgrades, and Enterprise contact-sales routing without requesting live billing execution.
---

# Subscription Upgrade Help

## Intent: helpdesk-subscription-upgrade-help
### User request patterns
- upgrade my X-HR subscription
- compare X-Basic X-Standard and X-Enterprise
- switch between monthly and annual billing
- add a payment card before subscribing
- contact sales for X-Enterprise

### Retrieval tags
- helpdesk
- subscription
- plans
- billing
- upgrade
- direct-answer

### Answer objective
Explain the current subscription packages and where authoritative pricing is shown.

### Instructions
- Answer directly without calling executable tools.
- Never quote a fixed X-Standard price from this skill. Company-effective pricing is supplied by the subscription service and can vary.

### Direct answer
1. Open [Explore Plans]({{explore_plans_url}}).
2. Compare the current packages:
   - **X-Basic**: the free entry plan. The page shows its current employee allowance and included features.
   - **X-Standard**: the paid self-service plan with monthly and annual billing. The displayed amount is the company-effective price returned for the selected billing cycle.
   - **X-Enterprise**: a tailored plan that routes to contact sales.
3. For annual X-Standard pricing, X-HR displays a monthly equivalent for comparison while checkout keeps the annual billing option.
4. Select the required plan and continue to checkout.

Admins can manage the company's default payment card from Billing even when there is no active subscription. Without an active subscription, Billing shows payment-method management only.

**Common issues**
- No plan or upgrade action: confirm the user has Admin access.
- Billing setup failed: verify the card details or contact Support.
- Employee limit reached: review the People-page upgrade notice and current company allowance.
