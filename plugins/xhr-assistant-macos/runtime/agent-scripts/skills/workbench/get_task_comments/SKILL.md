---
name: get-task-comments
description: Retrieve comments and discussion history for a specific Workbench task.
side_effect: read
---

# Get Task Comments

## Intent: get-task-comments
### User request patterns
- show comments for task
- view discussion on task
- get task comments thread

### Retrieval tags
- workbench
- task-comments
- comments-list
- discussion
- task-history

### Instructions
- `task_id` is required and must be a valid UUID.
- If `task_id` is unknown and only a task name or keyword is provided, run `python skills/workbench/get_tasks/scripts/get_tasks.py --name "<task title or keyword>" --page-number 0` to resolve `task_id`.
- Returns paginated list of comments with author details, creation timestamp, text, and attached documents.

### Required arguments
- `task_id`: UUID of the task.

### Optional arguments
- `page`: Page number (0-based, default 0).
- `size`: Page size (default 20).

### Execution
```text
python skills/workbench/get_task_comments/scripts/get_task_comments.py --task-id <UUID> [--page 0] [--size 20]
```
