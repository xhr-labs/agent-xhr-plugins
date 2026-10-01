---
name: workbench-manage-wiki-comments
description: List, reply to, create, resolve, or delete comment threads on xHR Workbench wiki pages (project wiki or company wiki). Use when the user asks to see wiki comments, answer/reply to a comment thread, create a comment, or mark a wiki comment as resolved.
side_effect: write
---

# Manage Wiki Comments

## Intent: workbench-manage-wiki-comments
### User request patterns
- show comments on wiki page
- list wiki comments
- answer wiki comment
- reply to comment on wiki page
- add comment to wiki
- resolve wiki comment thread
- delete wiki comment


### Retrieval tags
- workbench
- wiki
- wiki-comments
- comment-threads
- reply-comment
- answer-comment
- resolve-thread

### Instructions
- **Action Selection**:
  - `list`: Show all comment threads and replies on a wiki page (default).
  - `reply`: Reply to / answer an existing comment thread on a wiki page.
  - `create_thread`: Create a new comment thread on selected text or page.
  - `resolve`: Mark a comment thread as resolved (or unresolve with --resolved false).
  - `delete`: Delete a wiki comment by ID.
- **Input Verification Rule**:
  - `project_id` (or `project_name`, or `--scope company` for company wiki) and `page_id` (or `page_title`) are required.
  - For `reply` and `resolve`, `thread_id` is required (if unknown, run `manage_wiki_comments.py --action list` first).
  - For `reply` and `create_thread`, `content` (comment text) is required.
- **Mandatory User Confirmation & Turn Boundary (for write actions: reply, create_thread, resolve, delete)**:
  - Adding, replying to, resolving, or deleting comments modifies wiki collaboration data. Before executing manage_wiki_comments.py with --confirmed true, **ALWAYS** present a preview:
    - **Wiki Page**: <page title> (<page UUID>)
    - **Thread / Comment**: <thread UUID or comment ID>
    - **Action**: <Reply to thread | Create comment thread | Resolve thread | Delete comment>
    - **Message / Content**: <message content> (if applicable)
  - Ask the user: "Do you confirm submitting this wiki comment/reply/action on page '[Page Title]'/?".
  - **STOP and wait for explicit user confirmation** (e.g. "yes", "confirm", "dong y") in a subsequent turn before executing. **DO NOT execute the modification script in the same turn as presenting the preview.*

### Required arguments
- `page_id` or `page_title`.
- `thread_id` and `content` for `action: reply`.
- `content` for `action: create_thread`.
- `thread_id` for `action: resolve`.
- `comment_id` for `action: delete`.


### Optional arguments
- `action`: `list` (default) | `reply` | `create_thread` | `resolve` | `delete`.
- `project_id` or `project_name` (unless `--scope company`).
- `selected_text`: Selected text snippet for new thread.
- `from_pos`: Start character offset (default: 0).
- `to_pos`: End character offset (default: 0).
- `resolved`: `true` (default for resolve) | `false`.
- `scope`: `project` (default) | `company`.
- `confirmed`: Explicit confirmation flag (`true`).

### Execution
```text
# List comment threads on a wiki page
python skills/workbench/manage_wiki_comments/scripts/manage_wiki_comments.py --action list --project-id <UUID> --page-id <UUID>

# Reply to a comment thread (after confirmation)
python skills/workbench/manage_wiki_comments/scripts/manage_wiki_comments.py --action reply --project-id <UUID> --page-id <UUID> --thread-id <UUID> --content "<reply message>" --confirmed true

# Create a new comment thread (after confirmation)
python skills/workbench/manage_wiki_comments/scripts/manage_wiki_comments.py --action create_thread --project-id <UUID> --page-id <UUID> --content "<comment text>" --selected-text "<snippet>" --confirmed true

# Resolve a comment thread (after confirmation)
python skills/workbench/manage_wiki_comments/scripts/manage_wiki_comments.py --action resolve --project-id <UUID> --page-id <UUID> --thread-id <UUID> --resolved true --confirmed true
```
