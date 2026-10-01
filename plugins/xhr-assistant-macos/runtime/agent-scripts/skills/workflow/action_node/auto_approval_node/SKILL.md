---
name: workflow-action-auto-approval-node
description: Leaf guide for building an auto-approval STEP node.
---

# Auto Approval Node Template

Build a `STEP` node containing one `AUTO_APPROVAL_TASK`.

## Required STEP fields
- `id`: `node_step_<6 lowercase hex chars>`
- `type`: `STEP`
- `label`: string
- `step_execution_mode`: `SERIAL`
- `tasks`: one `AUTO_APPROVAL_TASK`
- `target_step_id`: next node id or `end`

## AUTO_APPROVAL_TASK fields
- `id`: `<step_id>_action_<uuid_with_underscores>`
- `type`: `AUTO_APPROVAL_TASK`
- `actors`: `null`
- `execution_mode`: `null`
- `completion_mode`: `null`
