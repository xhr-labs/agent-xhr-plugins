---
name: manage-linked-tasks
description: Link or unlink Workbench tasks with dependency relations (blocks, depends_on / is_blocked_by, parent_of, child_of, related_to, duplicate_of, caused_by) or view existing linked tasks.
side_effect: write
---

# Manage Linked Tasks

## Intent: manage-linked-tasks
### User request patterns
- link task A to task B
- mark task as blocked by another task
- show linked tasks or blockers for this task
- remove task link / unlink tasks

### Retrieval tags
- workbench
- linked-tasks
- task-dependencies
- blockers
- relates-to
- blocked-by
- parent-task
- subtask

### Instructions
- **Input Verification Rule**:
  - `task_id` and `target_task_id` must be valid UUIDs (if only task names or task numbers are known, run `python skills/workbench/get_tasks/scripts/get_tasks.py --name "<task title or keyword>" --page-number 0` to resolve task UUIDs).
  - Use `action`: `get` (default), `link` (add link), or `unlink` (remove link).
  - When linking, `relation_type` accepts `blocks`, `depends_on` (or `is_blocked_by`), `parent_of`, `child_of`, `related_to` (or `relates_to`), `duplicate_of`, or `caused_by` (defaults to `related_to`).
- **Mandatory User Confirmation & Turn Boundary (for link / unlink)**:
  - For write actions (`link` or `unlink`), **ALWAYS** present a preview:
    - **Source Task**: `<source task number & name> (<source task UUID>)`
    - **Target Task**: `<target task number & name> (<target task UUID>)`
    - **Relation**: `<relation_type>`
    - **Action**: `<link or unlink>`
  - Ask the user: *"Do you confirm linking/unlinking these tasks?"*.
  - **STOP and wait for explicit user confirmation** (e.g. "yes", "confirm", "đồng ý") in a subsequent turn before executing. **DO NOT execute the script in the same turn as presenting the preview.**

### Required arguments
- `task_id`: UUID of the primary task.

### Optional arguments
- `action`: `get` | `link` | `unlink` (default `get`).
- `target_task_id`: UUID of the linked target task (required for `link` / `unlink`).
- `relation_type`: Relationship type (`blocks`, `depends_on` / `is_blocked_by`, `parent_of`, `child_of`, `related_to` / `relates_to`, `duplicate_of`, `caused_by`).

### Execution
```text
python skills/workbench/manage_linked_tasks/scripts/manage_linked_tasks.py --task-id <UUID> [--action <get|link|unlink>] [--target-task-id <UUID>] [--relation-type <blocks|depends_on|is_blocked_by|parent_of|child_of|related_to|duplicate_of|caused_by>]
```
