---
name: move-wiki-page
description: Reorder or move a wiki page within the document tree (change parent page or position among siblings).
side_effect: write
---

# Move Wiki Page

## Intent: move-wiki-page
### User request patterns
- move wiki page to another folder/parent
- reorder wiki pages in hierarchy
- change page parent in wiki

### Retrieval tags
- workbench
- wiki
- move-page
- reorder-wiki
- hierarchy

### Instructions
- **Input Verification Rule**:
  - `page_id` is required and must be a valid UUID.
  - `parent_id`: Target parent page UUID (or empty string to move to root).
  - `prev_id` / `next_id`: UUIDs of sibling pages for precise ordering.
  - `project_id`: Provide project UUID for Project Wiki; omit for Company Wiki.
- **Mandatory User Confirmation & Turn Boundary**:
  - Before executing `move_wiki_page.py`, **ALWAYS** present a preview:
    - **Page ID / Title**: `<page title or ID>`
    - **Target Position**: `<New Parent / Root / Sibling Order>`
  - Ask the user: *"Do you confirm moving this wiki page?"*.
  - **STOP and wait for explicit user confirmation** (e.g. "yes", "confirm", "đồng ý") in a subsequent turn before executing. **DO NOT execute the script in the same turn as presenting the preview.**

### Required arguments
- `page_id`: UUID of the page to move.

### Optional arguments
- `parent_id`: Target parent UUID.
- `prev_id`: Sibling page UUID directly before target position.
- `next_id`: Sibling page UUID directly after target position.
- `project_id`: Project UUID (omit for Company Wiki).

### Execution
```text
python skills/workbench/move_wiki_page/scripts/move_wiki_page.py --page-id <UUID> [--parent-id <UUID>] [--project-id <UUID>]
```
