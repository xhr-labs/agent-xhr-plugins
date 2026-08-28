---
name: workbench-company-page-hierarchy
description: Retrieve the company wiki page hierarchy in Workbench. Use when the user asks to browse, inspect, or locate pages in the company wiki tree.
---

# Company Page Hierarchy

Use this executable leaf when the user wants the company wiki tree.

# Intent Map

## Intent: browse-company-wiki-hierarchy
### User request patterns
- show the company wiki hierarchy
- browse the company wiki tree
- what pages exist in the company wiki?
- list company wiki sections
- help me find a company wiki page

### Retrieval tags
- workbench
- wiki
- company-page
- hierarchy

### Answer objective
Return the company wiki hierarchy so the user can discover or confirm the correct page before fetching content.

### Instructions
- Use this leaf when the company page ID is unknown or the user wants to browse the tree.
- Prefer this hierarchy leaf before `company_page_content` when the target page is not yet identified.
- Keep page titles and IDs visible when the helper returns them.
- Use the executable leaf rather than inferring company wiki structure.

### Required arguments
- None.

### Execution
- Script entrypoint: `skills/workbench/company_page_hierarchy/scripts/company_page_hierarchy.py`
- Use the restricted command-style `exec` surface with the explicit runtime-relative wrapper path and CLI flags when available.
