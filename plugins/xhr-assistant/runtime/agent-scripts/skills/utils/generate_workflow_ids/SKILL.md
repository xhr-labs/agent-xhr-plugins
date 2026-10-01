---
name: utils-generate-workflow-ids
description: Generate workflow step/action identifiers. Use when the user or workflow runtime needs fresh low-risk IDs and the agent should execute skills/utils/generate_workflow_ids/scripts/generate_workflow_ids.py.
---

# Generate workflow IDs

This file is an executable leaf skill entrypoint.

## Runtime entrypoint
- Execute `skills/utils/generate_workflow_ids/scripts/generate_workflow_ids.py`.
- Do not search for another child skill under this directory.

Run the utils script via the restricted command-style exec surface:

```text
python skills/utils/generate_workflow_ids/scripts/generate_workflow_ids.py [--step-id <optional non-negative count>] [--action-id <optional non-negative count>]
```

If both counts are omitted, run the script without extra flags.

Rules:
- `step-id` and `action-id` are counts, not existing IDs.
- Omit or pass `0` for any list you do not need.
- Do not fabricate IDs in natural language; rely on tool output.
- Do not mention internal tool names in the user-facing reply.
