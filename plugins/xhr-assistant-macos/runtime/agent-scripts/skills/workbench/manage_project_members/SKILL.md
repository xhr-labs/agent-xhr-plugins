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
- For questions about Owner being absent from the Share dropdown or who can create sprints, read `skills/workbench/share_and_permissions/SKILL.md` and answer without changing membership.
- Owner may appear in existing member data, but it is not an assignable Share option. Do not execute `add` or `update_role` with `OWNER`, or remove/re-add an Owner to simulate an ownership transfer. The script accepting an enum is not evidence of a supported ownership-transfer workflow. Explain this limitation and direct ownership-delegation requests to support for confirmed options.
- **Input Verification Rule**:
  - `project_id` is required and must be a valid UUID (if unknown, run `python skills/workbench/show_project_overview/scripts/show_project_overview.py` to resolve `project_id`).
  - `action`: `list` (default), `add` (invite employee), `remove` (remove from project), or `update_role`.
  - `employee_id`: Required for `add`, `remove`, and `update_role` (if only employee name is known, run `python skills/employee/search_employees/scripts/search_employees.py --name "<name>"` to resolve `employee_id`).
  - `role`: `CONTRIBUTOR` (default) or `VIEWER` for invitations and role updates.
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
- `role`: Assignable collaborator role (`CONTRIBUTOR`, `VIEWER`).

### Execution
```text
python skills/workbench/manage_project_members/scripts/manage_project_members.py --project-id <UUID> [--action <list|add|remove|update_role>] [--employee-id <UUID>] [--role <CONTRIBUTOR|VIEWER>]
```
