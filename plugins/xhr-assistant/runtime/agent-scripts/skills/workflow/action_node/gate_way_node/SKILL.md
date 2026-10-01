---
name: workflow-action-gateway-node
description: Leaf guide for building an exclusive gateway node with exactly two transitions.
---

# Gateway Node Template

Build a `GATEWAY` node for conditional branching.

## Required GATEWAY fields
- `id`: `node_condition_<6 lowercase hex chars>`
- `type`: `GATEWAY`
- `label`: string
- `gateway_type`: `EXCLUSIVE`
- `transitions`: exactly two transition objects

## Transition object fields
- `target_step_id`: next node id
- `condition`: condition string or `null`
- `label`: string
- `is_default`: boolean

## Notes
- Gateway conditions may reference variables exposed by the selected trigger leaf.
- For more than two conditions, chain multiple gateway steps.
