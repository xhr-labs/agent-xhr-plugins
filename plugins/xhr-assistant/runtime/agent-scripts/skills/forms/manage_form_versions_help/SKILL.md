---
name: forms-manage-form-versions-help
description: Explain form draft, published, version, archive, and public-access behavior in X-HR. Use when the user asks how to edit a published form, create a draft version, publish a version, archive a form, or stop public access.
---

# Manage Form Versions Help

## Intent: forms-manage-form-versions-help
### User request patterns
- edit a published form
- create a draft version of a form
- publish a form version
- archive a form
- stop public access to a form

### Retrieval tags
- forms
- versions
- draft
- archive
- unpublish
- direct-answer

### Answer objective
Explain status-aware form editing and lifecycle actions.

### Instructions
- Answer directly without calling executable tools.
- Do not imply archived forms are permanently deleted.
- Explain that the live published version is isolated from edits until a draft is published.
- Do not promise a standalone unpublish action unless the current product surface or backend policy confirms it.

### Direct answer
Open [Forms]({{forms_url}}) and select the form.

- Draft forms can be edited and published.
- To change a published form, open **Edit** or **Manage versions** and work on the latest editable draft. Publishing that draft makes it the active version; editing the draft does not change the live published version.
- The current Forms frontend exposes public-link generation/regeneration, expiration, and password settings. It does not expose a standalone **Unpublish** client action. If the user asks to disable an existing public link, explain this product boundary and verify the tenant's supported backend/share policy instead of inventing a button.
- Use **Archive** when the form is no longer operational. X-HR asks for confirmation and removes normal edit/publish actions from archived forms; do not describe archive as permanent deletion.
- Submitted Data review is pinned to the active published version and is read-only. It is not the same as opening the form for draft editing.
- While a publish, archive, or version action is processing, wait for it to finish before starting another action.
