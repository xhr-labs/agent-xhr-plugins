---
name: workbench-get-task-detail
description: Fetch one Workbench task's full details by task UUID — description, status with ids, priority, dates, assignee, reporter, sprint, story points, linked tasks, custom fields, and timestamps. Use when the user asks what a specific task is about or needs any field the task list does not carry.
side_effect: read
---

# Get Task Detail

Use this executable leaf when the user needs the full record of one known task. The task LIST (`get_tasks`) returns summary rows only — the backend list API does not include `description`, `priority`, dates, or `assignee` — so any question about a task's content or attributes lands here.

# Intent Map

## Intent: get-workbench-task-detail
### User request patterns
- show the details of task T-12
- what is this task about?
- show the description of the login-page task
- check the due date and assignee of task X
- show linked tasks and custom fields of a task
- open task detail

### Retrieval tags
- workbench
- task
- detail
- description
- lookup

### Answer objective
Return the complete record of one task so the user (or a follow-up flow) has its description, status ids, priority, dates, people, sprint, story points, links, custom fields, and timestamps.

### Instructions
- `task_id` is required and must be a valid UUID. If only the task number, title, or a keyword is known, first run `python skills/workbench/get_tasks/scripts/get_tasks.py --name "<task title or keyword>" --page-number 0` and take `task_id` from the matching row.
- Present the fields the user asked about; keep `status_id` visible when a status change may follow (update flows can use it directly).
- Use the executable leaf rather than inventing task data.

### Required arguments
- `task_id` — UUID of the task.

### Execution
- Script entrypoint: `skills/workbench/get_task_detail/scripts/get_task_detail.py`
- Example execution: `python skills/workbench/get_task_detail/scripts/get_task_detail.py --task-id <task UUID>`
- Use the restricted command-style `exec` surface with the explicit runtime-relative wrapper path and CLI flags when available.
