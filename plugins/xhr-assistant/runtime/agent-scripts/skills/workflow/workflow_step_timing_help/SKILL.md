---
name: workflow-step-timing-help
description: Explain per-step trigger timing for date-based workflows. Use when the user asks how to configure workflow actions before, on, or after a reference date, create reminder chains, or interpret timing badges.
---

# Workflow Step Timing Help

## Intent: workflow-step-timing-help
### User request patterns
- set a workflow step before a date
- run an action on the reference date
- run an action after the reference date
- create multiple reminders around one date
- explain a workflow timing badge

### Retrieval tags
- workflow
- trigger-timing
- before
- after
- reminder-chain
- direct-answer

### Answer objective
Explain node-level timing in date-based workflows.

### Instructions
- Answer directly without calling executable tools.

### Direct answer
Open the date-based workflow step and configure **Trigger Timing**:

- **Before**: run the step a selected amount of time before the workflow reference date.
- **On**: run the step on the reference date.
- **After**: run the step after the reference date.

Each step has its own timing, so multiple reminders or actions can share one reference date. The workflow canvas displays a timing badge on configured steps.
