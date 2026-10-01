---
name: employee-helpdesk-submit-request
description: Submit an Employee Helpdesk request for the authenticated employee after reading the request type form, previewing the answers, and receiving explicit confirmation.
side_effect: write
idempotency: key
---

# Submit Employee Request

## Intent: employee-helpdesk-submit-request
### User request patterns
- submit an HR request
- create a salary certificate request
- submit my completed Employee Helpdesk form
- confirm and send this employee request

### Retrieval tags
- employee-helpdesk
- submit
- create
- salary-certificate
- write-action

### Answer objective
Create a request for the authenticated employee using an active request type version and answers that match the type's form contract.

### Instructions
1. Resolve the type with `get_request_types` (match `name`; use `id` and `version_number`). Never invent or reuse a type ID, key, or version; a type name is not an ID.
2. Read the form with `get_request_type --request-type-id <UUID>`. Build `answers` only from `answer_contract.fields`, using each `key` exactly. `SELECT` → one of `allowed_values`; `BOOLEAN` → JSON `true`/`false`; `DATE` → `YYYY-MM-DD`; text → string; `EMPLOYEE_REFERENCE` → employee UUID; `DOCUMENT_UPLOAD` → array of completed attachment intent UUIDs. Omit optional fields left blank.
3. Ask the user for every required field that is still missing. Do not fill required values yourself.
4. If a required `DOCUMENT_UPLOAD` field exists, files cannot be sent through chat: hand off to the app form and stop.
5. Present a preview: type name and version, each field label with its value, attachment state. STOP and wait for explicit confirmation in a later turn.
6. Execute once with `--idempotency-key <uuid>` you generate and keep; if the network result is ambiguous, retry once with the same key and body only when the user asks.
7. Backend validation errors (`FORM_ANSWERS_INVALID`, `REQUEST_TYPE_VERSION_INACTIVE`) are authoritative: report them and ask the user; do not retry with altered keys or values.
8. After success, report the returned `request_number`, `status`, and `id`; do not submit again to "check".

### Required arguments
- `request_type_id` (UUID)
- `request_type_version` (integer `version_number`)
- `answers_json` (JSON object keyed by form field keys)

### Optional arguments
- `completed_attachment_intent_ids`
- `idempotency_key`

### Execution
`python skills/employee_helpdesk/submit_request/scripts/submit_request.py --request-type-id <UUID> --request-type-version <n> --answers-json '{"purpose":"BANK_APPLICATION","addressee":"ACB","includeSalary":true}' --idempotency-key <uuid> [--completed-attachment-intent-ids <UUID,...>]`
