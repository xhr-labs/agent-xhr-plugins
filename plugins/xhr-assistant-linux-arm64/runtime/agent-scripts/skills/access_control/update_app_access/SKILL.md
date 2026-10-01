---
name: access-control-update-app-access
description: Change which platform groups can open an installed app, for example admin only or all employees. Use when the user wants to restrict or open app access, and the agent needs the runtime script at skills/access_control/update_app_access/scripts/update_app_access.py.
side_effect: write
idempotency: none
---

## Intent: update_app_access

### User request patterns
- make the Time-off app available to all employees
- restrict the payroll app to admins only
- change who can open an app
- hide an app from regular employees
- open an app up to HR managers

### Retrieval tags
app access, restrict app, open app, admin only, all employees, app visibility, app store settings

### Answer objective
Set the groups allowed to open the app and report the stored value read back after saving.

### Instructions
This file is an executable leaf skill entrypoint.

- Execute `skills/access_control/update_app_access/scripts/update_app_access.py`.
- Do not search for another child skill under this directory.

Before running:
- Confirm the app and the target groups with the user.
- Restricting an app hides it from everyone outside the listed groups; say so before applying it.

### Execution

```text
python skills/access_control/update_app_access/scripts/update_app_access.py --app "<app name, slug, or id>" --groups "<ADMIN|HR_MANAGER|EMPLOYEE[,...]|ALL_EMPLOYEES|UNRESTRICTED>"
```

### Required arguments
- `app`: app name, slug, or id.
- `groups`: comma-separated group names. Allowed values are `ADMIN`, `HR_MANAGER`, and `EMPLOYEE`. Use `ALL_EMPLOYEES` or `UNRESTRICTED` by itself to clear the stored group restriction.

Rules:
- Only `ADMIN`, `HR_MANAGER`, and `EMPLOYEE` are accepted. The API stores any other string without complaining, so the script rejects unknown values first.
- To open an app to every employee, use `EMPLOYEE` or clear the stored restriction with `ALL_EMPLOYEES` / `UNRESTRICTED` when the existing configuration should return to `groups: []`.
- App access cannot target one employee, one team, or one department. If the user asks for that, say the app-level setting is group-based and point at data-block permissions for finer control.
- This setting does not change what a user can see inside the app.
- Report the values the tool read back after saving, not the requested values.
- Do not mention internal tool names in the user-facing reply.
