---
name: timeoff-request-time-off-help
description: Answer direct how-to questions about requesting time off or applying for leave in X-HR. Use when the user asks how to request time off without requesting live submission.
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
**Instructions:**
1. Go to [Time Off → My Time Off]({{timeoff_url}})
2. Select Request Time Off and choose the Time Off Type
3. Select the start and end dates
4. Add reason/notes and upload supporting documents if required
5. Click "Submit Request"

Zero-day requests may be blocked because a request needs a valid leave duration. Cancellation and other actions are shown only when the request status, policy, and your permissions allow them.

**Alternative way is asking Agent directly:**
- I want to submit a vacation request from date to date
- I want to submit a sick leave

**Prerequisites:** Employee must have available leave balance
**Common Errors & Solutions:**
- "Insufficient leave balance" → Check current balance in Time Off summary
- "Overlapping request" → Cancel existing request or modify dates
- "Action is hidden" → Check request status and whether cancellation or edits are allowed for that request
