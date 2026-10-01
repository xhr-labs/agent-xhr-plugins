---
name: allocation-management-create-custom-fields
description: Create the five custom fields required by Allocation Management after checking the current user has Admin permission, previewing existing definitions, and receiving explicit confirmation.
side_effect: write
idempotency: none
---

# Create Allocation Management Custom Fields

This file is an executable leaf skill entrypoint.

## Runtime entrypoint
- Execute `skills/allocation_management/create_allocation_custom_fields/scripts/create_allocation_custom_fields.py`.
- Do not search for another child skill under this directory.

## Intent: allocation-management-create-custom-fields
### User request patterns
- create the five custom fields for Allocation Management
- create FTE CAP PROD and SOURCE fields
- configure Allocation Management custom fields for my workspace
- check whether the Allocation custom fields already exist and create missing fields
- create the Allocation fields only if I am an Admin

### Retrieval tags
- allocation-management
- allocation-setup
- custom-fields
- create-custom-fields
- Admin
- permission
- write-action

### Answer objective
Safely create only the missing Allocation Management custom-field definitions for an Admin user and report existing, conflicting, created, and failed fields.

### Instructions
- This leaf performs a write action. Check the current user permission in the tool result and require explicit confirmation before executing with `confirm=true`.
- First execute without confirmation to produce the preview. Show the five definitions, existing matches, inactive fields, conflicts, and fields that would be created. Stop and ask the Admin to confirm.
- On the confirmed call, execute the tool once with `confirm=true`. Do not claim that fields were created unless the tool reports them in `created`.
- The tool refuses non-Admin users before making any API request. Do not suggest bypassing this check.
- The tool checks existing definitions using the exact `fieldCode + source + section` identity. It skips matching definitions and never updates, activates, deletes, or replaces existing fields.
- If an existing definition has the expected identity but a different type, report it as a conflict and do not modify it.
- If an existing matching definition is inactive or deleted, report it as inactive and do not create a duplicate or activate it automatically.
- The tool creates all definitions as active and optional. This avoids breaking employee or department forms before HR has populated values. Explain that field values and Allocation data refresh remain separate follow-up steps.
- The two `FTE` fields intentionally share the same field code but have different source and section values.
- `FTE` fields use `TEXT`, `CAP` and `PROD` use `BOOLEAN`, and `SOURCE` uses `TEXT` by default because Source Line choices are company-specific and must not be invented.
- If the Admin supplies one or more `source_choice` values, the tool creates `SOURCE` as a `SELECT` field with those exact choices. Do not invent or infer Source Line choices.
- Do not populate employee values, department values, or refresh Allocation data in this tool. After creation, guide the Admin to populate values and refresh existing installations.
- Keep internal matching details, API paths, request methods, and implementation terms out of user-facing replies.
- Do not mention internal tool names in the user-facing reply.

### Required arguments
- None for preview. The tool uses the current request context for Admin permission and workspace authentication.

### Optional arguments
- `confirm` - Boolean. Defaults to `false`; use `true` only after explicit user confirmation.
- `source_choice` - Repeatable Source Line choice. If supplied, creates the Department `SOURCE` field as `SELECT`; otherwise creates it as `TEXT`.

### Execution
```text
python skills/allocation_management/create_allocation_custom_fields/scripts/create_allocation_custom_fields.py [--confirm true|false] [--source-choice "<Source Line>"]
```
