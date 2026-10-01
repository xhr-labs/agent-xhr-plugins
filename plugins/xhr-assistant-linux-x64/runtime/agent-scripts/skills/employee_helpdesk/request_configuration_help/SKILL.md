---
name: employee-helpdesk-configuration-help
description: Answer direct how-to questions about the Employee Helpdesk request-type configuration screen, drafts, versions, publishing, archive and restore without calling tools.
---

# Request Configuration Help

## Intent: employee-helpdesk-configuration-help
### User request patterns
- explain Employee Helpdesk request types
- how do I create a request type in the app
- what is the difference between a draft and publishing
- explain request type drafts and versions
- what happens to existing requests when I publish or archive

### Retrieval tags
- employee-helpdesk
- request-types
- publishing
- configuration
- direct-answer

### Answer objective
Explain how HR managers configure the request catalog in the current app.

### Instructions
- Answer directly without calling executable tools; refer to `manage_request_type` when the user wants to create, edit, publish, archive, or restore.
- Describe only the app surface below. Queues are resolved internally: the app has no Queue Configuration screen and the creation wizard has no queue selector. Do not ask users for queue IDs or JSON.

### Direct answer
Request Types (Settings → Request types) lists types in Active, Drafts, and Archived tabs with search. "New request type" opens a three-step wizard: Details (name, description, instructions), Form fields (field key, type, label, required, options), Policy (attachment policy, SLA targets, default priority). You can "Create draft version" (saved, invisible to employees, editable later) or "Create and Publish" (activates immediately). The versions page of a type shows its history; from there you create a new draft when none exists, edit a draft, or publish it. Publishing activates the draft for new submissions while existing requests keep the version they were submitted with. Archive (retire) stops new submissions but preserves existing requests and history; Restore re-enables the type without publishing pending drafts. Duplicate seeds a new type from an existing version. Routing to the HR queue is configured internally, not on this screen.
