---
name: forms-audit-form-logs-help
description: Explain how to inspect form audit logs in X-HR. Use when the user asks who updated a form, whether an email was sent, when a form changed, or why audit history is incomplete.
---

# Form Audit Logs Help

## Intent: forms-audit-form-logs-help
### User request patterns
- view form audit logs
- check who updated a form
- confirm a form email was sent
- find when a form was changed
- load more form activity

### Retrieval tags
- forms
- audit-logs
- email
- activity
- direct-answer

### Answer objective
Explain the published-form audit-log view and its supported activity details.

### Instructions
- Answer directly without calling executable tools.
- Say that audit records are tenant-scoped, paginated, and fetched fresh when the dialog opens.
- Do not expose raw audit payloads or invent actions that are not displayed by the product.

### Direct answer
1. Open [Forms]({{forms_url}}) and open the actions menu for a published form.
2. Select **Audit logs**.
3. Review the activity details and select **Load more** when additional pages are available.

Form-update records show the update time and persisted actor name snapshot. Email-send records show the action, submitted time, recipient, actor name snapshot, language, and queued delivery status. Loading, empty, and error states are normal outcomes; a missing older page does not necessarily mean the form has no further activity.
