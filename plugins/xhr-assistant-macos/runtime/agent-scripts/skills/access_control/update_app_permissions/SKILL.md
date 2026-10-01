---
name: access-control-update-app-permissions
description: Grant or revoke read/write permission on one data block of an installed app for a relation such as company:hr or location:leader. Use when the user wants to change app permissions, and the agent needs the runtime script at skills/access_control/update_app_permissions/scripts/update_app_permissions.py.
side_effect: write
idempotency: none
---

## Intent: update_app_permissions

### User request patterns
- let HR view the time-off report
- give finance read access to the expense categories
- remove HR write access from the payroll configuration
- grant team leaders permission to edit timesheets
- change who can edit a data block in an app
- stop department heads from viewing an app section

### Retrieval tags
grant permission, revoke permission, app permission, data block, read access, write access, relation, role, authorization, allow, restrict

### Answer objective
Apply one permission change to one data block and report the practical effect in plain user language, using the values the API returns after saving.

### Instructions
This file is an executable leaf skill entrypoint.

- Execute `skills/access_control/update_app_permissions/scripts/update_app_permissions.py`.
- Do not search for another child skill under this directory.

Before running:
- Read the current configuration first with `skills/access_control/list_app_permissions/SKILL.md` when the block name or the relation is not already confirmed by tool output in this conversation.
- Confirm the change with the user before running. In the user-facing confirmation, say who will gain or lose access, what they can do, and where in the app. Do not present a technical checklist of `app`, `block`, `operation`, `action`, and `relations`.
- This changes the rule for a relation, not for one named person. If the user named one employee, confirm that the whole relation is the intended target.

### Execution

```text
python skills/access_control/update_app_permissions/scripts/update_app_permissions.py --app "<app name, slug, or id>" --block "<data block name>" --operation <read|write> --action <grant|revoke|replace> --relations "<relation[,relation]>"
```

### Required arguments
- `app`: app name, slug, or id, as shown by the list skill.
- `block`: the exact data block name, as shown by the list skill.
- `operation`: `read` or `write`.
- `action`: `grant` adds relations, `revoke` removes them, `replace` sets the exact list.
- `relations`: comma-separated relation identifiers such as `company:hr`, `location:leader`, `employee:owner`.

Rules:
- One block and one operation per run. For several changes, run the script once per change and report them together.
- The script sends the complete block list on every save, because the API resets any omitted block to `company:admin` only. Never build a payload by hand.
- `company:admin` cannot be revoked; the platform keeps it. Report this as a limitation rather than a failure.
- A relation outside the block's selectable list is rejected before the request is sent; offer the selectable relations instead of retrying.
- Granting `write` does not grant `read`. If the user expects the relation to also see the block, grant `read` as a second, separate change.
- Report `relations_before` and `relations_after` from the tool output; do not claim a change the output does not show.
- Do not mention internal tool names in the user-facing reply.
- Do not output a "Reference:" section by default. If useful, put raw ids in one short parenthetical after the plain explanation.
- Translate common relation ids for the user: `company:member` = all employees/company members, `company:hr` = HR, `company:finance` = Finance, `company:admin` = administrators, `employee:owner` = the employee themself, `location:leader` = location leaders, `location:hr` = location HR.
- Translate operations for the user: `read` = view, `write` = edit/manage.
