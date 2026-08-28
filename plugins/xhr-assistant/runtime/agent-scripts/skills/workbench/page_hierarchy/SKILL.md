---
name: workbench-page-hierarchy
description: Retrieve a Workbench project's wiki page hierarchy by project ID. Use when the user asks to browse, inspect, or locate pages within a specific project wiki.
---

# Page Hierarchy

Use this executable leaf when the user wants the page tree for a specific project wiki.

# Intent Map

## Intent: browse-project-wiki-hierarchy
### User request patterns
- show the wiki hierarchy for project Alpha
- browse the page tree for project 456
- what pages exist in this project wiki?
- list project wiki sections
- help me find a page in this project wiki

### Retrieval tags
- workbench
- wiki
- project-page
- hierarchy

### Answer objective
Return the project wiki hierarchy so the user can discover or confirm the correct page before fetching content.

### Instructions
- Require a concrete `project_id` before execution.
- If the project is known by name but not by ID, resolve it first with `show_project_overview`.
- Use this leaf when the project page ID is unknown or the user wants to browse the tree.
- Prefer this hierarchy leaf before `page_content` when the target page is not yet identified.
- Keep page titles and IDs visible when the helper returns them.
- Use the executable leaf rather than inferring project wiki structure.

### Required arguments
- `project_id` — project id whose wiki hierarchy should be returned.

### Execution
- Script entrypoint: `skills/workbench/page_hierarchy/scripts/page_hierarchy.py`
- Use the restricted command-style `exec` surface with the explicit runtime-relative wrapper path and CLI flags when available.
