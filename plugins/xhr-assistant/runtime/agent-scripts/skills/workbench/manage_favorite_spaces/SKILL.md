---
name: workbench-manage-favorite-spaces
description: List, pin/add, or remove favorite spaces (projects) in xHR Workbench. Use when the user asks to view favorite spaces, add/pin a project to favorites, or remove/unpin a project from favorites.
side_effect: write
---

# Manage Favorite Spaces

## Intent: workbench-manage-favorite-spaces
### User request patterns
- show my favorite spaces
- list favorite projects
- add project to favorites
- pin space to favorites
- remove project from favorites
- unpin space from favorites

### Retrieval tags
- workbench
- favorite-spaces
- pin-space
- favorite-project
- sidebar-favorites
- unpin-space

### Instructions
- **Action Selection**:
  - `list`: Show all favorite spaces for current user (default).
  - `add`: Add/pin a project space to favorites.
  - `remove`: Remove/unpin a project space from favorites.
- **Input Verification Rule**:
  - For `add` or `remove`, `project_id` or `project_name` is required (if unknown, run `python skills/workbench/show_project_overview/scripts/show_project_overview.py` to resolve).
- **Mandatory User Confirmation & Turn Boundary (for add / remove)**:
  - Adding or removing a favorite space modifies user navigation shortcuts. Before executing `manage_favorite_spaces.py` with `--confirmed true`, **ALWAYS** present a preview:
    - **Project / Space**: `<project name> (<project UUID>)`
    - **Action**: `<Add to favorites or Remove from favorites>`
  - Ask the user: *"Do you confirm adding/removing project '[Project Name]' to/from your favorite spaces?"*.
  - **STOP and wait for explicit user confirmation** (e.g. "yes", "confirm", "đồng ý") in a subsequent turn before executing. **DO NOT execute the modification script in the same turn as presenting the preview.**

### Required arguments
- None for `action: list`.
- `project_id` or `project_name` for `action: add` and `action: remove`.

### Optional arguments
- `action`: `list` (default) | `add` | `remove`.
- `page`: Page index (default: 0).
- `size`: Page size (default: 20).
- `confirmed`: Explicit confirmation flag (`true`).

### Execution
```text
# List favorite spaces
python skills/workbench/manage_favorite_spaces/scripts/manage_favorite_spaces.py --action list

# Add project to favorites (after confirmation)
python skills/workbench/manage_favorite_spaces/scripts/manage_favorite_spaces.py --action add --project-id <UUID> --confirmed true

# Remove project from favorites (after confirmation)
python skills/workbench/manage_favorite_spaces/scripts/manage_favorite_spaces.py --action remove --project-id <UUID> --confirmed true
```
