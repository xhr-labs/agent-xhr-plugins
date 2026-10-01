---
name: workbench-get-wiki
description: Resolve and fetch Workbench wiki content across company wiki and project/space wiki flows. Use when the user asks to read, open, fetch, or browse wiki pages but the correct page path, page_id, or project_id may still need to be resolved through hierarchy and project lookup steps.
---

# Get Wiki

Use this workflow leaf when the user wants wiki content but the flow must first determine whether the target is in the company wiki or in a project/space wiki, then resolve the right identifiers before fetching the page content.

# Intent Map

## Intent: get-wiki
### User request patterns
- open the company wiki page about onboarding
- show me the company wiki
- fetch the project wiki page for Platform Cleanup
- read the wiki for project Alpha
- open the space wiki page called API conventions
- show me the wiki for space Platform Cleanup
- read the wiki in space Alpha
- open the page Release Flow in space Core Platform
- show me the space wiki tree so I can pick the page
- show me the wiki tree so I can pick the page
- get the wiki content for this company page
- read the project wiki article about release flow
- open the wiki page in the Payments space
- fetch the space article about onboarding flow

### Retrieval tags
- workbench
- wiki
- company-wiki
- project-wiki
- page-resolution
- hierarchy
- content

### Answer objective
Return the correct Workbench wiki content only after resolving whether the request targets company wiki or project/space wiki, then resolving the required identifiers and disambiguating the requested page.

### Instructions
- Treat this as a workflow leaf, not a single API lookup.
- First determine whether the user is referring to:
  1. company wiki
  2. project wiki / space wiki
- Do not invent `project_id` or `page_id`.
- Keep any resolved `project_id`, page title, and `page_id` visible in the response so follow-up steps stay grounded.
- If multiple pages match a mentioned title, ask the user to confirm the intended page before fetching content.
- If the user did not provide enough information to identify a specific page, show hierarchy results and ask the user to pick.
- Prefer hierarchy first, content second, unless the flow already has concrete identifiers.

## Workflow mode: company_wiki
Use this mode when the user explicitly mentions company wiki, company page, company article, or wording that clearly points to the company-wide wiki instead of a project or space.

### Company wiki resolution rules
- If the flow already has a concrete `page_id`, fetch content directly with `company_page_content`.
- If `page_id` is missing, run the company hierarchy helper first:
  - `python skills/workbench/company_page_hierarchy/scripts/company_page_hierarchy.py`
- If the user already mentions a page title or recognizable page name:
  - inspect the returned company hierarchy
  - pick the matching page candidate
  - keep the matched title and `page_id` visible
  - ask the user to confirm the page before fetching content if there is any ambiguity
- If the user does not mention any page title:
  - show the company hierarchy result in a concise, navigable way
  - ask the user which page they want opened
  - stop there until the user identifies the intended page
- If multiple pages match, ask the user to confirm the intended page before fetching content.
- If no matching page title is found, say so clearly and ask the user to provide another page title.
- Do not auto-select a company wiki page from hierarchy when the user has not explicitly identified the page yet, even if there is only one obvious candidate.
- After the user confirms the intended page, fetch content with:
  - `python skills/workbench/company_page_content/scripts/company_page_content.py --page-id <page-id>`

## Workflow mode: project_or_space_wiki
Use this mode when the user explicitly mentions a project wiki, a space wiki, a project name, or wording that clearly implies the wiki belongs to a specific Workbench project/space.

### Project/space wiki resolution rules
- If the project/space is not yet known, ask the user for the concrete project or space name before continuing.
- Do not proceed to project lookup, hierarchy lookup, page matching, or content fetch until the project/space name is clear.
- If the user mentions a concrete project or space name, first resolve `project_id` with:
  - `python skills/workbench/show_project_overview/scripts/show_project_overview.py --project-name "<project or space name>"`
- Keep the resolved project name and `project_id` visible.
- If multiple projects match, ask the user to confirm the intended project before continuing.
- Once `project_id` is known, if `page_id` is still unknown, fetch the project wiki hierarchy with:
  - `python skills/workbench/page_hierarchy/scripts/page_hierarchy.py --project-id <project-id>`
- If the user already mentions a page title:
  - inspect the returned hierarchy for the matching page
  - keep the matched page title and `page_id` visible
  - ask the user to confirm the intended page before fetching content if there is any ambiguity
- If the user does not mention a page title:
  - show the hierarchy for that project/space
  - ask the user which page they want opened
  - stop there until the user identifies the intended page
- If multiple pages match, ask the user to confirm the intended page before fetching content.
- If no matching page title is found, say so clearly and ask the user to provide another page title.
- Do not auto-select a project/space wiki page from hierarchy when the user has not explicitly identified the page yet, even if there is only one obvious candidate.
- After the user confirms the intended page, fetch content with:
  - `python skills/workbench/page_content/scripts/page_content.py --project-id <project-id> --page-id <page-id>`

## Clarification rules
- If the user only says things like `open wiki`, `read wiki`, `show me the wiki`, or `open the space wiki` and does not specify enough scope for company vs project/space or does not give the concrete space/project name, ask a short clarification question first.
- Do not default company wiki when the scope is ambiguous.
- If the user mentions a project/space wiki but omits the project/space name, ask for the project/space name before doing hierarchy lookup.
- If the hierarchy response is large, summarize the most relevant candidate pages instead of dumping noisy raw output.
- If no matching page title is found in the hierarchy, say so clearly and ask the user whether to browse the visible hierarchy or provide another page title.

### Execution
- Company hierarchy: `python skills/workbench/company_page_hierarchy/scripts/company_page_hierarchy.py`
- Company page content: `python skills/workbench/company_page_content/scripts/company_page_content.py --page-id <page-id>`
- Project lookup: `python skills/workbench/show_project_overview/scripts/show_project_overview.py --project-name "<project or space name>"`
- Project hierarchy: `python skills/workbench/page_hierarchy/scripts/page_hierarchy.py --project-id <project-id>`
- Project page content: `python skills/workbench/page_content/scripts/page_content.py --project-id <project-id> --page-id <page-id>`
