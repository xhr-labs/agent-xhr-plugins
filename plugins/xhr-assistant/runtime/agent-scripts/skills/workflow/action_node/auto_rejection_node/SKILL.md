---
name: workflow-action-auto-rejection-node
description: Leaf guide for building an auto-rejection STEP node.
---

# Auto Rejection Node Template

Build a `STEP` node containing one `AUTO_REJECTION_TASK`.

## Required STEP fields
- `id`: `node_step_<6 lowercase hex chars>`
- `type`: `STEP`
- `label`: string
- `step_execution_mode`: `SERIAL`
- `tasks`: one `AUTO_REJECTION_TASK`
- `target_step_id`: next node id or `end`

## AUTO_REJECTION_TASK fields
- `id`: `<step_id>_action_<uuid_with_underscores>`
- `type`: `AUTO_REJECTION_TASK`
- `actors`: `null`
- `execution_mode`: `null`
- `completion_mode`: `null`
