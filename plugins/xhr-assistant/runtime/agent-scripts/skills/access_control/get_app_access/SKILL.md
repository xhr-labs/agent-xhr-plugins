---
name: access-control-get-app-access
description: Show which platform groups can open an installed app. Use when the user asks who has access to an app, and the agent needs the runtime script at skills/access_control/get_app_access/scripts/get_app_access.py.
side_effect: read
---

## Intent: get_app_access

### User request patterns
- who can open the Time-off app
- check whether the payroll app is admin only
- show the app access setting for an app
- is this app visible to all employees
- list which apps are restricted to admins

### Retrieval tags
app access, who can open, app visibility, admin only, all employees, app store settings, restricted app

### Answer objective
Report the groups allowed to open the requested app, and say plainly whether it is open to all employees or restricted.

### Instructions
This file is an executable leaf skill entrypoint.

- Execute `skills/access_control/get_app_access/scripts/get_app_access.py`.
- Do not search for another child skill under this directory.

### Execution

```text
python skills/access_control/get_app_access/scripts/get_app_access.py [--app "<optional app name, slug, or id>"]
```

Rules:
- Omit `--app` to review every installed app.
- An empty group list means no group restriction is stored, which the app UI shows as all employees.
- App access only decides who can open the app. It does not decide what they can see inside; that is data-block permissions.
- Do not invent group names; rely on tool output.
- Do not mention internal tool names in the user-facing reply.
