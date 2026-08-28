---
name: delete-wiki-page
description: Permanently delete a wiki page from a project wiki or company wiki after explicit confirmation.
side_effect: write
---

# Delete Wiki Page

## Intent: delete-wiki-page
### User request patterns
- delete wiki page
- remove documentation page
- delete project wiki document

### Retrieval tags
- workbench
- wiki
- delete-page
- remove-doc

### Instructions
- **Input Verification Rule**:
  - `page_id` is required and must be a valid UUID.
  - `project_id`: Provide project UUID for Project Wiki; omit for Company Wiki.
- **Mandatory Deletion Warning & Turn Boundary**:
  - Deleting a wiki page is permanent and destructive. **ALWAYS** show the deletion warning first:
    - **Page Title / ID**: `<page title> (<page UUID>)`
    - **Scope**: `Project Wiki (<project name> (<project UUID>))` or `Company Wiki`
    - **Warning**: *"This action is permanent and cannot be undone."*
  - Ask the user: *"Are you sure you want to permanently delete this wiki page?"*.
  - **STOP and wait for explicit user confirmation** (e.g. "yes", "delete it", "xóa") in a subsequent turn before executing. **DO NOT execute the script in the same turn as presenting the warning.**

### Required arguments
- `page_id`: UUID of the page to delete.

### Optional arguments
- `title`: Title of the page for confirmation display.
- `project_id`: Project UUID (omit for Company Wiki).
- `confirmed`: Explicit confirmation flag.

### Execution
```text
python skills/workbench/delete_wiki_page/scripts/delete_wiki_page.py --page-id <UUID> [--project-id <UUID>] --confirmed true
```
