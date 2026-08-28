---
name: create-wiki-page
description: Create a new wiki document page in a project wiki or company-wide wiki workspace.
side_effect: write
---

# Create Wiki Page

## Intent: create-wiki-page
### User request patterns
- create wiki page
- add new documentation page
- create subpage in wiki

### Retrieval tags
- workbench
- wiki
- create-page
- new-doc
- knowledge-base

### Instructions
- **Input Verification Rule**:
  - `title` is required.
  - `project_id`: Provide project UUID to create a Project Wiki page; omit `project_id` to create a Company-wide Wiki page.
  - `parent_id`: Provide parent page UUID to create as a nested subpage.
  - `content`: Optional Markdown content.
- **Mandatory User Confirmation & Turn Boundary**:
  - Before executing `create_wiki_page.py`, **ALWAYS** present a preview:
    - **Page Title**: `<title>`
    - **Scope**: `Project Wiki (<project name> (<project UUID>))` or `Company Wiki`
    - **Parent Page**: `<parent page title or "Root">`
    - **Content Preview**: `<summary of content>`
  - Ask the user: *"Do you confirm creating this wiki page?"*.
  - **STOP and wait for explicit user confirmation** (e.g. "yes", "confirm", "đồng ý") in a subsequent turn before executing. **DO NOT execute the script in the same turn as presenting the preview.**

### Required arguments
- `title`: Page title.

### Optional arguments
- `content`: Page Markdown content.
- `project_id`: Project UUID (omit for Company Wiki).
- `parent_id`: Parent page UUID for nested hierarchy.

### Execution
```text
python skills/workbench/create_wiki_page/scripts/create_wiki_page.py --title "<title>" [--content "<markdown>"] [--project-id <UUID>] [--parent-id <UUID>]
```
