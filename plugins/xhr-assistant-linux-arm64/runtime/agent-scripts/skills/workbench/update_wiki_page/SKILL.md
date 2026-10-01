---
name: update-wiki-page
description: Update title or content for an existing Wiki document page in a project wiki or company wiki.
side_effect: write
---

# Update Wiki Page

## Intent: update-wiki-page
### User request patterns
- update wiki page
- edit wiki document
- change page title or content

### Retrieval tags
- workbench
- wiki
- update-page
- edit-doc
- knowledge-base

### Instructions
- **Input Verification Rule**:
  - `page_id` is required and must be a valid UUID.
  - `project_id`: Provide project UUID if updating a Project Wiki page; omit for Company Wiki.
  - At least `title` or `content` must be provided.
- **Mandatory User Confirmation & Turn Boundary**:
  - Before executing `update_wiki_page.py`, **ALWAYS** present a preview:
    - **Page ID / Title**: `<page title or ID>`
    - **Proposed Changes**: `<new title and/or content outline>`
  - Ask the user: *"Do you confirm updating this wiki page with these changes?"*.
  - **STOP and wait for explicit user confirmation** (e.g. "yes", "confirm", "đồng ý") in a subsequent turn before executing. **DO NOT execute the script in the same turn as presenting the preview.**

### Required arguments
- `page_id`: UUID of the page to update.

### Optional arguments
- `title`: New title.
- `content`: New Markdown content.
- `project_id`: Project UUID (omit for Company Wiki).

### Execution
```text
python skills/workbench/update_wiki_page/scripts/update_wiki_page.py --page-id <UUID> [--title "<title>"] [--content "<markdown>"] [--project-id <UUID>]
```
