---
name: workflow-action-approval-node
description: Leaf guide for building an approval STEP node with an APPROVAL_TASK.
---

# Approval Node Template

Build a `STEP` node containing one `APPROVAL_TASK`.

## Required STEP fields
- `id`: `node_step_<6 lowercase hex chars>`
- `type`: `STEP`
- `label`: string
- `step_execution_mode`: `SERIAL`
- `tasks`: one `APPROVAL_TASK`
- `target_step_id`: next node id or `end`

## APPROVAL_TASK fields
- `id`: `<step_id>_action_<uuid_with_underscores>`
- `type`: `APPROVAL_TASK`
- `actors`: requested approvers only
- `execution_mode`: `PARALLEL` or `SERIAL`
- `completion_mode`: `ANY` or `ALL`

## Helper dependencies
- Allowed actors include workflow roles or a concrete employee id.
- If the user provides an approver name, resolve that employee id with the employee search skill.

## Decision mapping
- All approvers must approve -> `PARALLEL` + `ALL`
- Any approver can decide -> `PARALLEL` + `ANY`
- One after another -> `SERIAL` + `ALL`
