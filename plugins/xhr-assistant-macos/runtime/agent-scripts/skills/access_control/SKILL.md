---
name: access-control
description: Access control skill index for App Store app access and app data-block permissions - who can open an installed app, and which relations can read or write each data block.
---

# Access control skill index

Use this file to choose the correct executable access-control skill.

## Navigation contract
- This file is a parent/index node only.
- Read the child `SKILL.md` entrypoint below to continue.
- Do not execute this directory as a script skill.
- Execute only the child leaf scripts referenced by the chosen leaf `SKILL.md` file.

## Scope of this domain
This domain owns the two configuration layers that every installed app shares:
- App access: which platform groups can open an app at all.
- Data-block permissions: which relations can read or write each data block of an app.

## User-facing wording
- Explain permission changes in product language first: who gains or loses access, what they can do, and where in the app.
- Avoid leading with raw argument names such as `app`, `block`, `operation`, `action`, or `relations`. Use those only as internal execution arguments.
- Keep relation ids such as `company:member` only when they help disambiguate the audience; pair them with a plain label such as "all employees" or "HR".
- Ask confirmation in one plain sentence. Example: "I'll let all employees view the Time-off Report in Time-off. Please confirm before I apply it."
- After saving, report the practical result first. Example: "Done. All employees can now view the Time-off Report in Time-off."

## Out of scope - route elsewhere
- Making someone a manager, HR, or team leader: organization and roles, not this domain.
- Sharing one specific project, task, or data room with one person: `skills/workbench/SKILL.md` or `skills/vdr/SKILL.md`.
- Choosing who approves a request: `skills/workflow/SKILL.md`.
- Installing or removing an app: `skills/appstore/SKILL.md`.
- What a specific block means for one app: that app's own domain index.

## Child entrypoints
- `skills/access_control/app_permissions_help/SKILL.md`
- `skills/access_control/check_my_app_access/SKILL.md`
- `skills/access_control/get_app_access/SKILL.md`
- `skills/access_control/list_app_permissions/SKILL.md`
- `skills/access_control/update_app_access/SKILL.md`
- `skills/access_control/update_app_permissions/SKILL.md`
