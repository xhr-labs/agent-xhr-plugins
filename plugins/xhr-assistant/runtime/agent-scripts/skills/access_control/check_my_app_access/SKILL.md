---
name: access-control-check-my-app-access
description: Check the signed-in user's own effective read and write access to each data block of an app. Use when the user cannot see or edit part of an app, and the agent needs the runtime script at skills/access_control/check_my_app_access/scripts/check_my_app_access.py.
side_effect: read
---

## Intent: check_my_app_access

### User request patterns
- why can I not see the time-off report
- check my access to the payroll app
- do I have permission to edit this app section
- I get no data in an app section
- show my effective permissions for an app

### Retrieval tags
my access, effective permission, cannot see, cannot edit, access denied, permission check, troubleshoot access

### Answer objective
Report, per data block, whether the signed-in user can currently read and write, and name the block that is blocking them.

### Instructions
This file is an executable leaf skill entrypoint.

- Execute `skills/access_control/check_my_app_access/scripts/check_my_app_access.py`.
- Do not search for another child skill under this directory.

### Execution

```text
python skills/access_control/check_my_app_access/scripts/check_my_app_access.py --app "<app name, slug, or id>"
```

### Required arguments
- `app`: app name, slug, or id.

Rules:
- This returns the effective access of the signed-in user only. It cannot be run for another employee; if the user asks about someone else, say so and offer the configured policy instead via `skills/access_control/list_app_permissions/SKILL.md`.
- A block the user cannot read is the likely cause of an empty section. Pair the finding with the configured policy before suggesting a change.
- Access can be blocked at the app level too. If the user cannot open the app at all, check app access as well.
- Do not mention internal tool names in the user-facing reply.
