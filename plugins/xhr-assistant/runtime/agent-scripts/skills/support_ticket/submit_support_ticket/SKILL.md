---
name: support-ticket-submit-support-ticket
description: Submit a support ticket or feature request after collecting required details and explicit confirmation. Use when the user asks to submit a support ticket, request a new feature, or send a feature request for them.
---

# Submit support ticket

Use this executable/orchestration leaf when the user asks to submit a support ticket or feature request.

# Intent Map

## Intent: submit-support-ticket
### User request patterns
- Submit a support ticket for me
- I want to request a new feature
- Send new feature request for me

### Retrieval tags
- support-ticket
- support
- feature-request
- submit
- confirmation-required

### Answer objective
Handle support-ticket and feature-request submission requests by collecting the required details first, then submitting only after explicit user confirmation.

### Instructions
- This workflow applies only when the user requests to submit a support ticket or feature request.
- You must first ask for the required details: `subject` and `description`.
- If the user already provided one of those fields, only ask for the missing one.
- Derive the submission type from intent:
  - Use the normal support-ticket topic when the user asks for help with an issue.
  - Use the feature-request topic when the user asks to request a new feature.
- You must confirm with the user before submission.
- You must not call `sendSupportTicket` without explicit user confirmation.
- Never submit the ticket automatically.
- Do not invent subject lines, issue descriptions, or success states.
- Do not mention internal tool names in the user-facing reply.

### Execution
- After collecting `subject` and `description` and receiving explicit confirmation, run:
  - `sendSupportTicket {"topic": "<support or feature-request>", "subject": "<confirmed subject>", "description": "<confirmed description>"}`
