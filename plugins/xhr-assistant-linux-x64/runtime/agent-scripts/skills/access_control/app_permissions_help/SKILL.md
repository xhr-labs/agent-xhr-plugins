---
name: access-control-app-permissions-help
description: Explain how app access and app data-block permissions work in X-HR, and which layer to change for a given request. Use when the user asks how app permissions work rather than asking to read or change a specific setting.
side_effect: read
---

## Intent: app_permissions_help

### User request patterns
- how do app permissions work
- what is the difference between app access and permissions
- explain data blocks and relations
- where do I manage who can see what in an app
- what does company:hr mean in app permissions

### Retrieval tags
app permissions explained, app access, data block, relation, rebac, authorization model, permission layers, how to grant access

### Answer objective
Explain the permission layers, name the right layer for the user's goal, and hand off to the skill or domain that changes it.

### Instructions
Answer from this file. Do not execute a script for this intent.
- Explain with non-technical wording first. Introduce terms like relation or data block only after a plain explanation.
- Prefer examples such as "HR can view the Time-off Report" over raw triples like `block=time_off_report`, `operation=read`, `relation=company:hr`.

### The layers

1. App access decides who can open an app at all. It is group-based: `ADMIN`, `HR_MANAGER`, `EMPLOYEE`, or an unrestricted empty group list. It cannot target one person, team, or department.
2. Data-block permissions decide, inside an app, which relations can read and which can write each block. A block is a named section of the app such as a report, a configuration area, or the permissions page itself.
3. Organization relations decide who actually matches a relation: who is HR, who leads a team, who belongs to a location.
4. Object-level sharing and approvals decide access to one specific record, and live in the owning domain.

A relation grant is a rule, not a grant to a named person. Whether one employee gains access depends on whether they hold that relation.

### Relations
Relations are `<scope>:<role>` identifiers such as `company:admin`, `company:hr`, `company:finance`, `company:member`, `location:hr`, `location:leader`, `location:member`, `employee:owner`. Each block exposes its own selectable list, so always read the block's list instead of assuming a relation is available.

### Rules worth stating to the user
- `company:admin` always keeps read and write; it cannot be revoked.
- Some blocks support read only. Write cannot be granted there.
- Granting write does not grant read. They are set separately.
- App access and data-block permissions are independent. Opening app access does not reveal a block, and granting a block does not let someone open the app.

### Routing
- Read current settings: `skills/access_control/list_app_permissions/SKILL.md`, `skills/access_control/get_app_access/SKILL.md`.
- Change settings: `skills/access_control/update_app_permissions/SKILL.md`, `skills/access_control/update_app_access/SKILL.md`.
- The user cannot see something and wants to know why: `skills/access_control/check_my_app_access/SKILL.md`.
- Make someone HR, a manager, or a team leader: organization and roles, outside this domain.
- Share one project, task, or data room: `skills/workbench/SKILL.md`, `skills/vdr/SKILL.md`.
- Decide who approves a request: `skills/workflow/SKILL.md`.
- Install or remove an app: `skills/appstore/SKILL.md`.
