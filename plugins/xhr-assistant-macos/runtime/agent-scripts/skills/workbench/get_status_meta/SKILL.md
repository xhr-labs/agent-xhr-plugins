---
name: workbench-get-status-meta
description: Retrieve Workbench status metadata before selecting status IDs, keys, or types. Use when the user asks about valid statuses or when another Workbench flow needs concrete status values.
---

# Get Status Meta

Use this executable leaf when the user needs valid status metadata before filtering tasks or creating work items.

# Intent Map

## Intent: list-valid-workbench-status-metadata
### User request patterns
- show available Workbench statuses
- what statuses can I use?
- get valid status ids
- list status metadata for task creation
- resolve the right status value

### Retrieval tags
- workbench
- status
- metadata
- lookup

### Answer objective
Return valid Workbench status metadata so downstream filters or write actions can use concrete status values.

### Instructions
- Use this leaf before task or project filters and create flows when the valid status values are not yet clear.
- Keep status names, keys, ids, and types visible whenever the helper returns them.
- Prefer this helper over guessing status values from informal labels.
- Preserve the underlying helper's accepted argument conventions, including `statusTypes` where required for compatibility.

### Supported arguments
- `status_type` — optional single status type.
- `statusTypes` — optional repeated status-type filter.

### Execution
- Script entrypoint: `skills/workbench/get_status_meta/scripts/get_status_meta.py`
- Use the restricted command-style `exec` surface with the explicit runtime-relative wrapper path and CLI flags when available.
