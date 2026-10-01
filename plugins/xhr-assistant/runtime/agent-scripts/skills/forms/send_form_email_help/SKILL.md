---
name: forms-send-form-email-help
description: Explain how to send an eligible published form by email in X-HR. Use when the user asks about form email invitations, recipients, templates, placeholders, attachments, or why email sending is unavailable.
---

# Send Form Email Help

## Intent: forms-send-form-email-help
### User request patterns
- send a form by email
- email a public form link
- customize a form email template
- add an attachment to a form email
- troubleshoot why form email is unavailable

### Retrieval tags
- forms
- email
- public-link
- attachments
- audit-logs
- direct-answer

### Answer objective
Explain the published-shareable form email flow and its eligibility rules.

### Instructions
- Answer directly without calling executable tools.
- Keep email invitations separate from internal Workflow or Task Hub assignments.
- Do not promise delivery; the UI records the request as queued and audit logs show the persisted send activity.

### Direct answer
1. Open [Forms]({{forms_url}}) and open the actions menu for a published, shareable form.
2. Select **Send via email**.
3. Enter the recipient email/name, subject, body, and any supported attachments. Up to five supported attachments can be added.
4. Use the supported `candidate_name`, `form_name`, and `form_link` placeholders when they are useful.
5. Send the message. X-HR resolves or creates the form's active public link before sending.

The action is unavailable for drafts, archived/deleted forms, Review forms, assigned-step forms, and forms where public sharing is disabled. Subject and body templates are reused by supported language; the current locale falls back to English when no localized template exists. Audit logs show the recipient, actor snapshot, locale, and queued status.
