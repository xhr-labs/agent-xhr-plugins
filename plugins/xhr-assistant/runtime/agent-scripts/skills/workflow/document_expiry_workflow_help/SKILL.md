---
name: workflow-document-expiry-workflow-help
description: Explain document-expiry automation in X-HR. Use when the user asks how to trigger reminders from employee document expiry, insert document fields into notification or email content, or configure document expiry step timing.
---

# Document Expiry Workflow Help

## Intent: workflow-document-expiry-workflow-help
### User request patterns
- create a document expiry reminder
- trigger a workflow before an employee document expires
- include the document name in a workflow email
- include the document link in an expiry notification
- send several reminders around a document expiry date

### Retrieval tags
- workflow
- document-expiry
- email
- reminder
- direct-answer

### Answer objective
Explain the document expiry event, available content fields, and timing.

### Instructions
- Answer directly without calling executable tools.

### Direct answer
Create a date-based workflow and select the **Document expiry** event. Use the document effective-to or expiry date as the reference date.

Configure each action step to run before, on, or after expiry. Notification and email content can use document event fields such as the document name, expiry date, and document URL when those fields are provided by the event.
