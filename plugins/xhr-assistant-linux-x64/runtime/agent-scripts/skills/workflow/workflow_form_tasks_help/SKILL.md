---
name: workflow-form-tasks-help
description: Explain how forms are assigned and completed through workflows. Use when the user asks about Fill Form actions, onboarding forms, review steps, subject employee context, or previous-step visibility in Task Hub.
---

# Workflow Form Tasks Help

## Intent: workflow-form-tasks-help
### User request patterns
- add a fill form task to a workflow
- assign an onboarding form in a workflow
- assign a review form step
- show previous review answers to a reviewer
- explain form completion from Task Hub

### Retrieval tags
- workflow
- forms
- fill-form
- onboarding
- review-task
- direct-answer

### Answer objective
Explain workflow form assignment and task-scoped completion.

### Instructions
- Answer directly without calling executable tools.

### Direct answer
In [Workflows]({{workflows_url}}), add a **Fill form** action to a workflow step, choose the form, and assign its recipients.

Normal fill-form tasks allow the assigned user to complete the form from Task Hub. Onboarding form actions collect employee profile data for an onboarding process. Review forms can assign separate stages to different reviewers; only the assigned stage is editable, while permitted completed stages appear as read-only context.

The completed form submission remains linked to the workflow and subject employee for reporting.
