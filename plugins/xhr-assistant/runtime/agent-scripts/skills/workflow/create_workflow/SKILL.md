---
name: workflow-create-workflow
description: Executable leaf for submitting the final workflow payload after trigger and steps have been prepared.
---

# Create Workflow

This is the executable workflow submission entrypoint.

## Preconditions
Before execution:
1. Select the trigger by reading the trigger-node guidance.
2. Build the workflow steps using the action-node and generate-steps guidance.
3. Generate compliant workflow IDs.
4. Confirm the final workflow arguments with the user before submission.

## Script entrypoint
- `skills/workflow/create_workflow/scripts/create_workflow.py`

## Execution style
Use the restricted command-style `exec` surface with explicit runtime-relative script path and CLI flags when available.

## Required arguments
- `eventKey`: workflow trigger event key
- `steps`: workflow steps payload
