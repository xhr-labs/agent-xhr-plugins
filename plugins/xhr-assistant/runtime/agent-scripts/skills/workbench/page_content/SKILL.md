---
name: workbench-page-content
description: Retrieve a specific Workbench project wiki page by project ID and page ID. Use when the user asks for the content of a known project wiki page.
---

# Page Content

Use this executable leaf when the user wants a known project wiki page.

# Intent Map

## Intent: fetch-project-page-content
### User request patterns
- show the wiki page with id 123 in project 456
- open this project wiki page
- get the content for page 789 in project Alpha
- fetch that known project wiki page
- read this project wiki article

### Retrieval tags
- workbench
- wiki
- project-page
- content

### Answer objective
Return the content of the requested project wiki page using a concrete `project_id` and `page_id`.

### Instructions
- Require concrete `project_id` and `page_id` values before execution.
- If `project_id` is missing, resolve it first with `show_project_overview`.
- If `page_id` is missing, use `page_hierarchy` first to discover candidate pages.
- Do not invent project IDs or page IDs.
- Keep the selected identifiers visible in the response so follow-up requests stay grounded.
- Use the executable leaf instead of fabricating wiki content.

### Required arguments
- `project_id` — project id that owns the page.
- `page_id` — wiki page id to fetch.

### Execution
- Script entrypoint: `skills/workbench/page_content/scripts/page_content.py`
- Use the restricted command-style `exec` surface with the explicit runtime-relative wrapper path and CLI flags when available.
