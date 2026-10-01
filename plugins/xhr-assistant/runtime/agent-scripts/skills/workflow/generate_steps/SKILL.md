---
name: workflow-generate-steps
description: Leaf guide for chaining workflow nodes into a valid `steps` list and generating compliant IDs.
---

# Generate Workflow Steps

Use this guide to construct the final `steps` list.

## Chaining rules
- `steps` must be a list of node objects connected via `transitions` for `GATEWAY` nodes or `target_step_id` for `STEP` nodes.
- Read the selected action-node leaves before constructing node payloads.

## ID generation
- `step_id` format: `node_${type}_${idFragment}`
- `action_id` format: `${step_id}_action_${uuid_with_underscores}`
- Generate new IDs every time; never reuse example IDs.

## Helper dependency
- Use the workflow-id utility when you need the official ID-generation helper.
