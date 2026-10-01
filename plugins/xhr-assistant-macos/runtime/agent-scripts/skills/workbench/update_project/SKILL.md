---
name: update-project
description: Update project name, description, status, start/target dates, icon, color, or enable/disable Sprint planning in Workbench.
side_effect: write
---

# Update Project

## Intent: update-project
### User request patterns
- update project
- rename project
- change project dates or status
- update project icon and color
- enable sprint for this project
- enable sprint for project ML, testing
- turn on sprint planning for project
- disable sprint in project
- bật sprint cho project
- kích hoạt tính năng sprint cho dự án

### Retrieval tags
- workbench
- update-project
- edit-project
- project-settings
- space-settings
- enable-sprint
- sprint-settings
- toggle-sprint

### Instructions
- **Enable/Disable Sprint Planning Rule**:
  - When the user asks to **enable** or **turn on** sprints for a project (e.g. `enable sprint for this project ML, testing`), use this skill with `--enable-sprint true`. Do NOT call `create_sprint`.
- **Input Verification Rule**:
  - `project_id` is required and must be a valid UUID (if unknown, run `python skills/workbench/show_project_overview/scripts/show_project_overview.py --project-name "<name>"` to resolve `project_id`).
  - At least one field to update must be provided.
  - `status_id` must be a valid project status UUID (resolve via `get_project_status_meta` if needed).
- **Mandatory User Confirmation & Turn Boundary**:
  - Before executing `update_project.py`, **ALWAYS** present a preview:
    - **Project**: `<project name or ID>`
    - **Proposed Changes**: `<list of changed fields and new values>`
  - Ask the user: *"Do you confirm updating project '[Project Name]' with these changes?"*.
  - **STOP and wait for explicit user confirmation** (e.g. "yes", "confirm", "đồng ý") in a subsequent turn before executing. **DO NOT execute the script in the same turn as presenting the preview.**

### Required arguments
- `project_id`: UUID of the project to update.

### Optional arguments
- `project_name`: New project name.
- `description`: New project description.
- `status_id`: UUID of project status.
- `start_date`: Start date (`YYYY-MM-DD`).
- `target_date`: Target/end date (`YYYY-MM-DD`).
- `icon`: Project icon identifier.
- `color`: Project color hex / name.
- `enable_sprint`: Boolean (`true` or `false`) to enable or disable Sprint planning.

### Execution
```text
python skills/workbench/update_project/scripts/update_project.py --project-id <UUID> [--project-name "<name>"] [--enable-sprint true|false] [--status-id <UUID>] [--target-date <YYYY-MM-DD>]
```
