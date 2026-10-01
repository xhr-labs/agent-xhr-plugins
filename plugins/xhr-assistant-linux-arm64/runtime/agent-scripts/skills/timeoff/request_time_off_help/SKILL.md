---
name: timeoff-request-time-off-help
description: Answer direct how-to questions about requesting, calculating, tracking, and cancelling leave in X-HR. Use when the user asks for guidance without requesting live submission.
---

# Request Time Off Help

Use this direct-answer leaf when the user asks about request time off help.

# Intent Map

## Intent: timeoff-request-time-off-help
### User request patterns
- How to request time off or apply for leave (vacation, sick leave)?
- Apply for maternity leave through Time Off
- Why can't I submit a zero-day leave request?
- Why can't I cancel a leave request?
- Why is my requested duration different from the date range?
- Why is my available balance lower than my total balance?

### Retrieval tags
- timeoff
- leave
- request
- vacation
- sick-leave
- maternity-leave
- cancellation
- direct-answer

### Answer objective
Answer directly with the documented steps for requesting time off.

### Instructions
- Answer directly in text using the guidance below.
- Do not call executable tools for this skill.

### Direct answer
1. Open [My Time Off]({{timeoff_url}}) and select Request Time Off.
2. Choose a leave type that is available to you.
3. Select the start and end dates. A normal date range counts weekdays and excludes public holidays for your work location.
4. If the request is partial-day, choose the daily options shown in the form. A full day is 1 day; morning, afternoon, and half day are 0.5 day.
5. Add notes or supporting documents if needed, then submit the request.

The request normally starts as pending. A pending request reserves days, so available balance can be lower than current balance before approval. Approval deducts the days; rejection releases the reservation; cancelling future approved leave restores the days.

Zero-day ranges, overlapping pending or approved requests, insufficient available balance, and leave types blocked for probation may be rejected. An approved request can be cancelled only before it starts; if it starts today or earlier in your timezone, it cannot be cancelled through this flow.

**Alternative way is asking Agent directly:**
- I want to submit a vacation request from date to date
- I want to submit a sick leave

**Prerequisites:** The employee needs a requestable leave type and enough available balance, unless the applicable policy permits advance leave.

**Common errors and solutions:**
- "Insufficient leave balance" -> Check available balance and pending requests, not only the gross balance.
- "The duration is unexpected" -> Check weekends, location holidays, and any partial-day selections.
- "Overlapping request" -> Review existing pending or approved requests and change the dates if appropriate.
- "Action is hidden" -> Check the request status and whether the leave has already started.
