---
name: workflow-date-based-workflow-help
description: Explain date-based workflow behavior in X-HR. Use when the user asks how to trigger automation from an employee or document date, configure a reference date and timezone, or create reminders before, on, or after that date without requesting live workflow creation.
---

# Date-Based Workflow Help

## Intent: workflow-date-based-workflow-help
### User request patterns
- create a date based workflow
- trigger a workflow from an employee date
- create reminders before a probation end date
- automate document expiry reminders
- configure the timezone for a date based workflow

### Retrieval tags
- workflow
- date-based
- reminder
- timezone
- direct-answer

### Answer objective
Explain date-based trigger configuration and its relationship to step timing.

### Instructions
- Answer directly without calling executable tools.
- Do not use the executable create-workflow leaf unless its payload contract supports the selected trigger type.

### Direct answer
When creating a workflow, choose **Date-based**, then select the event, its reference date field, and timezone.

The workflow-level setup identifies the reference date. The timing for each action is configured on the individual workflow step, allowing one workflow to run multiple reminders such as 7 days before, 1 day before, on the date, and after the date.

Typical date-based uses include probation-end reviews, employee lifecycle dates, and document expiry.
