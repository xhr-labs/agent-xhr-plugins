---
name: add-task-comment
description: Post a new comment or update message on a Workbench task, optionally attaching documents.
side_effect: write
---

# Add Task Comment

## Intent: add-task-comment
### User request patterns
- add comment to task
- comment on task
- post update on this workbench task

### Retrieval tags
- workbench
- task-comment
- comment
- add-comment
- discussion

### Instructions
- **Input Verification Rule**:
  - `task_id` is required and must be a valid UUID. If only task name/keyword is provided, run `python skills/workbench/get_tasks/scripts/get_tasks.py --name "<task title or keyword>" --page-number 0` to resolve `task_id`.
  - If task is unspecified, run `python skills/workbench/get_tasks/scripts/get_tasks.py --page-number 0` and ask user to specify the task.
  - `content` (comment text) or `document_ids` must be provided.
- **Mandatory User Confirmation & Turn Boundary**:
  - Before executing `add_task_comment.py`, **ALWAYS** present a preview:
    - **Task**: `<task number & task name>`
    - **Comment Content**: `"<comment text>"`
  - Ask the user: *"Do you confirm posting this comment on task '[Task Name]'?"*.
  - **STOP and wait for explicit user confirmation** (e.g. "yes", "confirm", "đồng ý") in a subsequent turn before executing. **DO NOT execute the script in the same turn as presenting the preview.**

### Required arguments
- `task_id`: UUID of the task to comment on.

### Optional arguments
- `content`: Text content of the comment.
- `document_id`: UUID of attached document (can be repeated).

### Execution
```text
python skills/workbench/add_task_comment/scripts/add_task_comment.py --task-id <UUID> --content "<comment text>"
```
