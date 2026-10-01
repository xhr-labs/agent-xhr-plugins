---
name: employee-helpdesk-get-request-type
description: Read one Employee Helpdesk request type's form fields, required answers, instructions, and attachment policy before submitting a request.
side_effect: read
---

# Get Request Type Form

## Intent: employee-helpdesk-get-request-type
### User request patterns
- what fields does the salary certificate request need
- show the form for request type <name>
- which answers are required before I submit
- check the form before creating my HR request

### Retrieval tags
- employee-helpdesk
- request-type
- form-schema
- required-fields
- read-action

### Answer objective
Return the exact form contract (field keys, types, required flags, allowed SELECT values) and attachment policy of one request type, so the submission preview uses real keys instead of guesses.

### Instructions
- Resolve the request type UUID with `get_request_types` first (match on `name`), then call this leaf. Never pass a type name or key as the ID.
- ALWAYS call this leaf before `submit_request`. The catalog list does not contain field keys.
- Build `answers` only from `answer_contract.fields`: use `key` exactly; `SELECT` takes one of `allowed_values`; `BOOLEAN` is a JSON boolean; `DATE` is `YYYY-MM-DD`; omit optional fields the user left blank.
- If `attachment_policy.max_count` is 0 the type accepts no files. If a `DOCUMENT_UPLOAD` field is required, the file must be uploaded in the app; chat cannot upload, so hand off to the app instead of inventing intent IDs.
- Do not use HR configuration tools (`manage_request_type get_version`) to read an employee form; this leaf is the employee-scoped source.

### Required arguments
- `request_type_id`

### Optional arguments
- `locale`

### Execution
`python skills/employee_helpdesk/get_request_type/scripts/get_request_type.py --request-type-id <UUID> [--locale <locale>]`
