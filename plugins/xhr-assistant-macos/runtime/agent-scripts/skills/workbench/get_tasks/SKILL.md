---
name: workbench-get-tasks
description: List Workbench tasks across projects with optional paging, project, assignee, task-name, status, priority, completion, and due-date filters. Use when the user asks for task lists, filtered project work, task lookup by name, or cross-project task lookup in Workbench.
---

# Get Tasks

Use this executable leaf when the user wants a filtered task list across projects.

# Intent Map

## Intent: list-or-filter-workbench-tasks
### User request patterns
- show tasks for project Alpha
- list all open Workbench tasks
- get tasks assigned to Kadek
- show tasks due this week
- list cross-project work items
- show my tasks
- what are my Workbench tasks?
- list my open tasks
- show my high priority tasks
- get my assigned work items
- what is assigned to me?
- show me my pending tasks?
- my tasks
- Show me task detail of task ID EM-1

### Retrieval tags
- workbench
- tasks
- list
- filter

### Answer objective
Return a filtered Workbench task list that matches the user's requested project, assignee, task-name, status, priority, completion, or due-date constraints, including the caller's own tasks when the intent is personal task lookup.

### Instructions
- This leaf returns summary rows only: the backend list API does not
  include `description`, `priority`, dates, or `assignee` (those come back
  as null). When the user asks for a task's details, resolve the `task_id`
  from the matching row (via `--name` if needed), then run
  `python skills/workbench/get_task_detail/scripts/get_task_detail.py --task-id <UUID>`.
- Extract any paging, completion, project, assignee, task-name, status, priority, or due-date filters the user already provided.
- Decide assignee scope explicitly:
  - If the user is asking about their own work with wording like `I`, `my`, `my tasks`, `assigned to me`, or another clearly self-referential phrasing, pass `mine=true`.
  - If the user is asking about another person, resolve or pass that person's `assignee_id` instead of using `mine=true`.
  - If an explicit `assignee_id` is already available, let that explicit `assignee_id` take precedence.
- `mine=true` means the app layer should fall back to the current user's `xhr-employee-id` when no explicit `assignee_id` is provided.
- If the user mentions a concrete project or space name but not a `project_id`, first run `python skills/workbench/show_project_overview/scripts/show_project_overview.py --project-name "<project or space name>"`, keep the resolved `project_id` visible, and then pass `--project-id <project-id>` into this leaf.
- If the user mentions a task title, task keyword, or task-number-like text that should narrow the result set, pass it through `--name`.
- If the user names a status informally and the valid status metadata is unclear, use `get_status_meta` first.
- Prefer the narrowest valid filter set that matches the request.
- Treat `recursive` as optional and default-off.
- Do not pass `recursive=true` unless the user or the current workflow explicitly requires fetching all pages or an exhaustive result set.
- When `recursive=true`, default `page_size` to `1000` unless the user explicitly asked for another page size.
- Pay attention to the returned `meta` block, especially `page_number`, `page_size`, `has_next`, `pages_fetched`, and `total_items_returned`, so you know whether another fetch is needed and how much data was collected.
- Use the executable leaf rather than inventing task data.

### Supported arguments
- `page_number` — optional result page number.
- `page_size` — optional page size, default `10`, or `1000` by default when `recursive=true`.
- `recursive` — optional boolean, default `false`. When `true`, keep fetching pages until `meta.has_next` is `false`.
- `include_completed` — optional boolean to include completed tasks.
- `mine` — optional boolean. When `true` and `assignee_id` is not provided, the helper falls back to the current user's `xhr-employee-id`.
- `priorities` — optional repeated priority filter.
- `status_id` — optional repeated status-id filter.
- `status_key` — optional repeated status-key filter.
- `status_name` — optional repeated status-name filter.
- `assignee_id` — optional repeated assignee-id filter.
- `project_id` — optional project id filter.
- `name` — optional task-name or keyword filter.
- `due_date` — optional due-date filter object or string supported by the underlying helper.

### Execution
- Script entrypoint: `skills/workbench/get_tasks/scripts/get_tasks.py`
- Example paginated execution: `python skills/workbench/get_tasks/scripts/get_tasks.py --page-number 0 --page-size 10`
- Example recursive execution: `python skills/workbench/get_tasks/scripts/get_tasks.py --project-id <project-id> --recursive true`
- Example caller-task execution: `python skills/workbench/get_tasks/scripts/get_tasks.py --mine true --page-number 0`
- Example other-person execution: `python skills/workbench/get_tasks/scripts/get_tasks.py --assignee-id <employee-id> --page-number 0`
- Example name-filter execution: `python skills/workbench/get_tasks/scripts/get_tasks.py --name "<task title or keyword>" --page-number 0`
- Use the restricted command-style `exec` surface with the explicit runtime-relative wrapper path and CLI flags when available.
