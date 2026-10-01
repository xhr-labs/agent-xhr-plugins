---
name: timeoff-configure-time-off-help
description: Answer direct questions about setting up Time Off types, policies, balances, and holiday-aware leave rules. Use when the user asks how to get started without requesting a live configuration action.
---

# Configure Time Off Help

## Intent: timeoff-configure-time-off-help
### User request patterns
- How to configure time off policies, leave balances, and holiday calendars?
- How to get started with Timeoff/Leave
- Configure carry-over for leave
- Recalculate time off policy retroactively
- Set up maternity leave

### Retrieval tags
- timeoff
- leave
- configuration
- balances
- holiday-calendars
- carry-over
- retroactive
- maternity-leave
- direct-answer

### Answer objective
Answer directly with the documented steps for configuring time off.

### Instructions
- Answer directly in text using the guidance below.
- Do not call executable tools for this skill.

### Direct answer
Open [Time Off]({{timeoff_url}}) and use the relevant setup page:

1. Open **Time Off Types**. Create a type only if an appropriate type does not already exist. Set whether it is paid or unpaid, whether it is maternity leave, and whether it is limited or unlimited.
2. Open **Time Off Policies** and create a policy for each population that needs different rules. Set the location, optional employee type or eligibility filters, allowance, accrual period, accrual year, timing, proration, and effective dates.
3. Configure optional carry-over, advance leave, seniority bonus, and probation-request blocking only when the company policy requires them.
4. Use **Time Off Balances** for opening balances or deliberate balance corrections. Normal policy accrual creates ongoing credits automatically.
5. Review **App Permissions** if employees cannot request leave or managers cannot see and approve team requests.

Public holidays are taken from the employee's work location when a date-range request is calculated. A roster or shift setup is not required for normal Time Off requests.

**Prerequisites:** The user needs the appropriate Time Off configuration permission to change types, policies, or balances. Employees can use their own leave workflow without configuration access.

**Common errors and solutions:**

- "I cannot see the setup pages" -> Check Time Off configuration access.
- "An employee has no balance" -> Check the matching active policy, location, effective date, eligibility, and employee start date before adding a manual balance.
- "The balance is lower than expected" -> Check pending requests, approved leave, carry-over expiry, manual corrections, and retroactive recalculation.
- "The policy cannot be saved" -> Check for an overlapping policy with the same leave type, location, dates, and overlapping eligibility rules.
- "Probationary employees cannot request this type" -> Review the policy's probation-request setting and eligibility rules.
