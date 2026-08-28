---
name: workbench-show-project-overview
description: Retrieve Workbench project overview data and resolve project IDs from project names. Use when the user asks about a project, needs project lookup data, or another Workbench flow needs a concrete project ID.
---

# Show Project Overview

Use this executable leaf when the user needs project lookup data or a project overview.

# Intent Map

## Intent: show-or-resolve-project-overview
### User request patterns
- show the overview for project Alpha
- look up this Workbench project
- get the project id for Platform Cleanup
- find the project named Redesign
- show project details in Workbench
- show me projects overview
- show me overview of AI project
- project overview
- show me project
- show all space overview
- space overview

### Retrieval tags
- workbench
- project
- overview
- lookup

### Answer objective
Return Workbench project overview data and preserve any resolved `project_id` so downstream flows can reuse it.

### Instructions
- Use this leaf when the user asks about project details or when another flow needs a concrete `project_id`.
- If the user provides a project name, pass it through so the helper can resolve matching projects.
- Keep resolved project names and IDs visible in the answer.
- If multiple projects match, ask the user to confirm the intended project before continuing into dependent flows.
- Treat `recursive` as optional and default-off.
- Do not pass `recursive=true` unless the user or the current workflow explicitly requires fetching all pages or an exhaustive result set.
- When `recursive=true`, default `page_size` to `1000` unless the user explicitly asked for another page size.
- Pay attention to the returned `meta` block, especially `page_number`, `page_size`, `has_next`, `pages_fetched`, and `total_items_returned`, so you know whether another fetch is needed and how much data was collected.
- Use the executable leaf rather than inventing project metadata.

### Supported arguments
- `project_name` — optional project name filter.
- `page_number` — optional result page number.
- `page_size` — optional page size, default `10`, or `1000` by default when `recursive=true`.
- `recursive` — optional boolean, default `false`. When `true`, keep fetching pages until `meta.has_next` is `false`.

### Execution
- Script entrypoint: `skills/workbench/show_project_overview/scripts/show_project_overview.py`
- Example paginated execution: `python skills/workbench/show_project_overview/scripts/show_project_overview.py --page-number 0 --page-size 10`
- Example recursive execution: `python skills/workbench/show_project_overview/scripts/show_project_overview.py --recursive true`
- Use the restricted command-style `exec` surface with the explicit runtime-relative wrapper path and CLI flags when available.
