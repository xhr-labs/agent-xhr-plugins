---
name: workbench-get-project-status-meta
description: Retrieve valid Workbench project status metadata before choosing a project status UUID for creation or updates. Use when the user asks which project statuses exist or when another Workbench project flow needs concrete project status values.
---

# Get Project Status Meta

Use this executable helper when the user needs valid project status metadata before creating a Workbench project or choosing a project-status UUID.

# Intent Map

## Intent: list-valid-workbench-project-status-metadata
### User request patterns
- show available Workbench project statuses
- what project statuses can I use?
- get valid project status ids
- list project status metadata for project creation
- resolve the right project status value

### Retrieval tags
- workbench
- project
- status
- metadata
- lookup

### Answer objective
Return valid Workbench project status metadata so downstream project flows can use concrete project-status UUIDs.

### Instructions
- Use this helper before project-create or project-update flows when the valid project status values are not yet clear.
- Keep project status names, ids, keys, and types visible whenever the helper returns them.
- Prefer this helper over guessing project status values from informal labels.
- When another flow needs a confirmed project status, tell the user to choose the exact `status_id` from `project_statuses`.

### Supported arguments
- None.

### Execution
- Script entrypoint: `skills/workbench/get_project_status_meta/scripts/get_project_status_meta.py`
- Use the restricted command-style `exec` surface with the explicit runtime-relative wrapper path and CLI flags when available.
