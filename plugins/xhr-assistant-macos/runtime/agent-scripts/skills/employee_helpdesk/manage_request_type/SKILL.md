---
name: employee-helpdesk-manage-request-type
description: Create, edit, publish, retire, restore, or inspect Employee Helpdesk request-type versions for an authorized HR manager.
side_effect: write
idempotency: key
read_actions: list_versions, get_version
---

# Manage Request Type

## Intent: employee-helpdesk-manage-request-type
### User request patterns
- create an Employee Helpdesk request type
- edit a request type draft
- publish a request type version
- retire or restore a request type
- view request type versions

### Retrieval tags
- employee-helpdesk
- request-types
- versions
- publish
- configuration
- write-action

### Answer objective
Apply one explicit request-type configuration operation with the correct root or draft version.

### Instructions
- Actions: `create`, `create_version`, `get_version`, `list_versions`, `update_draft`, `publish`, `retire`, `restore`.
- Resolve IDs only from reads: root `id` and root `version` from `list_request_types`; version `id`, `state` (DRAFT/ACTIVE) and version `version` from `list_versions` / `get_version`. Never guess UUIDs.
- The app wizard collects: name, description, instructions, form fields, attachment policy, SLA targets, default priority. Routing (`default_queue_id`) and privacy metadata are filled from the existing default queue and sensible defaults, not asked from the user. Do not ask the user for queues or raw JSON.
- Show the full draft/publish payload as a preview and STOP for explicit confirmation in a later turn. A request to preview or not save yet means no call.
- One backend validation error → report and ask; do not retry with altered payloads.

### Body contracts
- `create`: `--body-json '{"request_type_key": "UPPER_SNAKE", "draft": {...}}'`. Draft keys: `name`, `description`, `instructions`, `source_locale`, `form_schema` (`{"fields":[{"key","type","label","required","options?"}]}`; types SHORT_TEXT, LONG_TEXT, DATE, SELECT, BOOLEAN, EMPLOYEE_REFERENCE, DOCUMENT_UPLOAD), `default_queue_id` (from `list_queues`), `default_priority`, `first_response_target_seconds`, `resolution_target_seconds`, `attachment_policy` (`{"max_count":0}` or `{max_count, allowed_mime_types, max_file_size_bytes}`), `sensitivity_key`, `processing_purpose`, `lawful_basis_key`, `retention_policy_key`, `business_owner_employee_id`. Copy an existing type via `get_version` as the template. Creating returns a DRAFT; it is not visible to employees until published.
- `create_version`: no body; requires an active type without an existing draft. Returns the new DRAFT.
- `update_draft`: `--version-id <draft UUID> --if-match <draft.version> --body-json '{"draft": {...}}'` (full draft object).
- `publish`: `--version-id <draft UUID> --if-match <ROOT request type version from list_request_types>`. The script reads the draft's own `version` for `expected_draft_version` (pass `--expected-draft-version` only to override; it is the draft's `version` field, not `version_number`). On `VERSION_CONFLICT` refetch both versions once and re-preview; do not resend the same values. Activates the draft; existing requests keep their version, new submissions use the new one.
- `retire` / `restore`: `--if-match <ROOT request type version>`; no body. Retire stops new submissions and keeps existing requests and history; restore re-enables the type without publishing pending drafts.

### Execution
`python skills/employee_helpdesk/manage_request_type/scripts/manage_request_type.py --action <action> [--request-type-id <UUID>] [--version-id <UUID>] [--if-match <version>] [--expected-draft-version <n>] [--body-json '<json>']`
