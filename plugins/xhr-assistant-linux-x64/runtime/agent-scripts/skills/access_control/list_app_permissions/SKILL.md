---
name: access-control-list-app-permissions
description: Show the data-block permissions of installed apps - which relations can read or write each block. Use when the user wants to review app permissions, and the agent needs the runtime script at skills/access_control/list_app_permissions/scripts/list_app_permissions.py.
side_effect: read
---

## Intent: list_app_permissions

### User request patterns
- show the permissions of the Time-off app
- who can view the time-off report
- check which roles can edit payroll configuration
- review data block permissions for an app
- list the data blocks of an installed app
- find out what permissions an app has

### Retrieval tags
app permissions, data block, read access, write access, relation, role, app store, authorization, who can view, who can edit

### Answer objective
Report who can view or edit the requested app sections in plain user language, using data-block names and relation ids only when they clarify the exact rule.

### Instructions
This file is an executable leaf skill entrypoint.

- Execute `skills/access_control/list_app_permissions/scripts/list_app_permissions.py`.
- Do not search for another child skill under this directory.

### Execution

```text
python skills/access_control/list_app_permissions/scripts/list_app_permissions.py [--app "<optional app name, slug, or id>"]
```

Rules:
- Omit `--app` to review every installed app; pass it to focus on one app.
- Read the tool output before answering; never assume a block exists.
- `supported: false` on an operation means that operation cannot be granted on that block; say so instead of offering to grant it.
- `company:admin` is always present and cannot be revoked; do not present it as a removable grant.
- The relations shown are policy for a relation, not a grant to one named person. If the user asks about one employee, say that this shows the rule, not that person's effective access.
- Do not invent block names, relations, or app names; rely on tool output.
- Do not mention internal tool names in the user-facing reply.
- Do not present raw JSON-style field names such as `operation`, `action`, `relations`, or `data_blocks` to non-technical users.
- Translate common relation ids for the user: `company:member` = all employees/company members, `company:hr` = HR, `company:finance` = Finance, `company:admin` = administrators, `employee:owner` = the employee themself, `location:leader` = location leaders, `location:hr` = location HR.
