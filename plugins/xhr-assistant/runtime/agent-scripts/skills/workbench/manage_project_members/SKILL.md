---
name: manage-project-members
description: List, invite/add, remove, or update roles for project members and collaborators in Workbench.
side_effect: write
---

# Manage Project Members

## Intent: manage-project-members
### User request patterns
- add member to project
- invite employee to project
- list project members
- remove member from project
- change member role

### Retrieval tags
- workbench
- project-members
- collaborators
- add-member
- remove-member
- share-project

### Instructions
- **Input Verification Rule**:
  - `project_id` is required and must be a valid UUID (if unknown, run `python skills/workbench/show_project_overview/scripts/show_project_overview.py` to resolve `project_id`).
  - `action`: `list` (default), `add` (invite employee), `remove` (remove from project), or `update_role`.
  - `employee_id`: Required for `add`, `remove`, and `update_role` (if only employee name is known, run `python skills/employee/search_employees/scripts/search_employees.py --name "<name>"` to resolve `employee_id`).
  - `role`: `OWNER`, `CONTRIBUTOR` (default), or `VIEWER`.
- **Mandatory User Confirmation & Turn Boundary (for write actions)**:
  - Adding, removing, or updating roles for project members are write actions. Before executing `manage_project_members.py` with `add`, `remove`, or `update_role`, **ALWAYS** present a preview:
    - **Project**: `<project name>`
    - **Employee**: `<employee name>`
    - **Action / Role**: `<add as CONTRIBUTOR / remove / update role to VIEWER>`
  - Ask the user: *"Do you confirm [Action] for [Employee Name] in project '[Project Name]'?"*.
  - **STOP and wait for explicit user confirmation** (e.g. "yes", "confirm", "đồng ý") in a subsequent turn before executing. **DO NOT execute the script in the same turn as presenting the preview.**

### Required arguments
- `project_id`: UUID of the project.

### Optional arguments
- `action`: `list` | `add` | `remove` | `update_role`.
- `employee_id`: UUID of the employee.
- `role`: Role enum (`OWNER`, `CONTRIBUTOR`, `VIEWER`).

### Execution
```text
python skills/workbench/manage_project_members/scripts/manage_project_members.py --project-id <UUID> [--action <list|add|remove|update_role>] [--employee-id <UUID>] [--role <OWNER|CONTRIBUTOR|VIEWER>]
```
