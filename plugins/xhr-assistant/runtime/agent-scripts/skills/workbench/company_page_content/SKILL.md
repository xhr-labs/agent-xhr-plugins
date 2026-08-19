---
name: workbench-company-page-content
description: Retrieve a specific company wiki page by page ID in Workbench. Use when the user asks for the content of a known company wiki page.
---

# Company Page Content

Use this executable leaf when the user wants a known company wiki page.

# Intent Map

## Intent: fetch-company-page-content
### User request patterns
- show the company wiki page with id 123
- open this company page
- get the content for company page 456
- fetch that company wiki article
- read this known company wiki page

### Retrieval tags
- workbench
- wiki
- company-page
- content

### Answer objective
Return the content of the requested company wiki page using a concrete `page_id`.

### Instructions
- Require a concrete `page_id` before execution.
- If the page ID is missing, use `company_page_hierarchy` first to discover candidate pages.
- Do not invent page IDs.
- Keep the selected page ID visible in the response so follow-up requests stay grounded.
- Use the executable leaf instead of fabricating wiki content.

### Required arguments
- `page_id` — company wiki page id to fetch.

### Execution
- Script entrypoint: `skills/workbench/company_page_content/scripts/company_page_content.py`
- Use the restricted command-style `exec` surface with the explicit runtime-relative wrapper path and CLI flags when available.
