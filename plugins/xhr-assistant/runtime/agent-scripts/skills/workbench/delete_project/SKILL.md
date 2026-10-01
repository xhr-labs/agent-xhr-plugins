---
name: delete-project
description: Permanently delete a Workbench project after explicit user confirmation.
side_effect: write
---

# Delete Project

## Intent: delete-project
### User request patterns
- delete project
- remove project space
- delete entire workbench project

### Retrieval tags
- workbench
- delete-project
- remove-space
- project-lifecycle

### Instructions
- **Input Verification Rule**:
  - `project_id` is required and must be a valid UUID (if unknown, run `python skills/workbench/show_project_overview/scripts/show_project_overview.py` to resolve `project_id`).
- **Mandatory Deletion Warning & Turn Boundary**:
  - Project deletion is permanent and deletes all contained tasks, sprints, and wikis. **ALWAYS** show the destructive warning first:
    - **Project Name / ID**: `<project name or UUID>`
    - **Warning**: *"Deleting this project will permanently remove all associated tasks, sprints, and wiki pages. This action cannot be undone."*
  - Ask the user: *"Are you sure you want to permanently delete project '[Project Name]'?"*.
  - **STOP and wait for explicit user confirmation** (e.g. "yes", "delete it", "xóa") in a subsequent turn before executing. **DO NOT execute the delete script in the same turn as presenting the warning.**

### Required arguments
- `project_id`: UUID of the project to delete.

### Optional arguments
- `project_name`: Name of the project for confirmation display.
- `confirmed`: Explicit confirmation flag.

### Execution
```text
python skills/workbench/delete_project/scripts/delete_project.py --project-id <UUID> [--project-name "<name>"] --confirmed true
```
