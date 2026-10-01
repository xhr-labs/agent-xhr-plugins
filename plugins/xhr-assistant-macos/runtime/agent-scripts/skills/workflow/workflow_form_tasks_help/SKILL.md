---
name: workflow-form-tasks-help
description: Explain how forms are assigned and completed through workflows. Use when the user asks about Fill Form actions, workflow-based onboarding forms, review steps, subject employee context, or previous-step visibility in Task Hub. Do not use it as the primary answer for the onboarding form login-blocking setting.
---

# Workflow Form Tasks Help

## Intent: workflow-form-tasks-help
### User request patterns
- add a fill form task to a workflow
- assign an onboarding form in a workflow
- assign a review form step
- show previous review answers to a reviewer
- explain form completion from Task Hub
- distinguish workflow onboarding from login-blocking onboarding

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
- Distinguish a workflow-assigned onboarding task from the Onboarding form setting **Force to show form on logging in**. The latter is configured in Forms and does not require a separate workflow just to block platform access at login.

### Direct answer
In [Workflows]({{workflows_url}}), add a **Fill form** action to a workflow step, choose the form, and assign its recipients when the form should be triggered by an event or date, routed to selected recipients, or combined with approvals and other workflow steps.

For a login-blocking onboarding form, open [Forms]({{forms_url}}), choose an **Onboarding form**, and enable **Force to show form on logging in** in **Form setup**. That direct setting is separate from workflow assignment.

Normal fill-form tasks allow the assigned user to complete the form from Task Hub. Onboarding form actions collect employee profile data for an onboarding process. Review forms can assign separate stages to different reviewers; only the assigned stage is editable, while permitted completed stages appear as read-only context.

The completed form submission remains linked to the workflow and subject employee for reporting.
