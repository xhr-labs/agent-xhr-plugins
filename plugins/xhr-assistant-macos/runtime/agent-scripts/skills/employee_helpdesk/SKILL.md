---
name: employee-helpdesk
description: Handle Employee Helpdesk (Employee Requests) for employees and HR managers - HR request tickets such as salary or employment certificates, payroll questions, personal-information changes, request forms and submission, HR inbox case handling, request-type configuration, and HR request reports.
---

# Employee Helpdesk Skill Tree

Use this domain for the Employee Helpdesk app (Employee Requests service): HR request tickets (`ER-YYYY-NNNNNN`),
their request types and forms, the HR inbox, and request-type configuration.
Not this domain: company document storage (`documents`), DOCX generation (`document_generator`), generic forms (`forms`), leave (`timeoff`).

## Choose the caller role first
- The user talks about "my request" (first person), submitting or following up on their own ticket → **Employee leaves only**. Never fall back to HR leaves to read or act on the caller's own requests, and never use HR configuration leaves to read an employee form.
- The user acts as HR (inbox, assign, triage, resolve, configuration, reports) → **HR manager leaves**. The backend enforces ReBAC; a 403 means stop, not switch leaf.

## Employee leaves
- `skills/employee_helpdesk/request_overview_help/SKILL.md` — Explain Employee Helpdesk and its lifecycle.
- `skills/employee_helpdesk/submit_request_help/SKILL.md` — Explain how employees submit requests (how-to only).
- `skills/employee_helpdesk/request_status_help/SKILL.md` — Explain request statuses and employee actions.
- `skills/employee_helpdesk/get_request_types/SKILL.md` — List active request types available to the employee (names and IDs only).
- `skills/employee_helpdesk/get_request_type/SKILL.md` — Read one request type's form fields, required answers, and attachment policy. **Required before submit_request.**
- `skills/employee_helpdesk/list_my_requests/SKILL.md` — List the caller's requests; resolve `ER-…` ticket numbers to UUIDs here.
- `skills/employee_helpdesk/get_request/SKILL.md` — Read one of the caller's request details (UUID).
- `skills/employee_helpdesk/get_request_data/SKILL.md` — Read the caller's request messages, activities, attachments, or download links.
- `skills/employee_helpdesk/submit_request/SKILL.md` — Submit a request after form read, preview, and confirmation.
- `skills/employee_helpdesk/add_request_message/SKILL.md` — Add a public message to the caller's request after confirmation.

## HR manager leaves
- `skills/employee_helpdesk/hr_inbox_help/SKILL.md` — Explain HR inbox and case handling.
- `skills/employee_helpdesk/request_configuration_help/SKILL.md` — Explain request types, versions, and publishing.
- `skills/employee_helpdesk/request_reports_help/SKILL.md` — Explain HR request reports.
- `skills/employee_helpdesk/request_permissions_help/SKILL.md` — Explain employee versus HR manager access.
- `skills/employee_helpdesk/list_hr_requests/SKILL.md` — Search the tenant HR inbox; resolve `ER-…` numbers to UUIDs with `--search`.
- `skills/employee_helpdesk/get_hr_request/SKILL.md` — Read an HR request workspace, including `version` and `available_actions`.
- `skills/employee_helpdesk/get_hr_request_data/SKILL.md` — Read HR request conversations, activities, attachments, counts, and download links.
- `skills/employee_helpdesk/manage_hr_request/SKILL.md` — Perform HR case, collaboration, lifecycle, and attachment actions.
- `skills/employee_helpdesk/list_eligible_assignees/SKILL.md` — Find eligible HR assignees for a queue.
- `skills/employee_helpdesk/list_queues/SKILL.md` — List HR queues (backend routing; no app screen).
- `skills/employee_helpdesk/manage_queue/SKILL.md` — Create, update, or retire an HR queue (backend-only; no app screen).
- `skills/employee_helpdesk/list_request_types/SKILL.md` — List configured request types (root `id`, `version`, active flag).
- `skills/employee_helpdesk/manage_request_type/SKILL.md` — Create, edit, publish, retire, or restore request types.
- `skills/employee_helpdesk/get_hr_report_overview/SKILL.md` — Read the HR request overview report.
- `skills/employee_helpdesk/manage_request_privacy/SKILL.md` — Privacy operations and legal holds (separate permission; backend-only, no app screen).

## Scripts
- Every executable leaf lives at `skills/employee_helpdesk/<leaf>/scripts/<leaf>.py` (for example `skills/employee_helpdesk/get_request_types/scripts/get_request_types.py`). There is no `skills/employee_helpdesk/scripts/` directory. Identity (`--company-id`, `--employee-id`) comes from headers; never pass it.

## Identifiers, versions, and enums
- Every `--request-id`, `--request-type-id`, `--version-id`, `--queue-id`, `--assignee-id` is a UUID returned by a read tool. `ER-2026-000001` is a ticket number: resolve it with `list_my_requests` (employee) or `list_hr_requests --search ER-2026-000001` (HR) and use the `id` field. Never construct, reuse from memory, or guess a UUID; never use the caller's employee ID as a request ID.
- Every mutation on an existing object needs `--if-match <version>`: the numeric `version` from the latest detail read, or the `version` returned by the previous write. Scripts format the header; pass the plain number.
- Enums: `assignment` any|mine|unassigned · `sla_risk` normal|warning|breached · `view` inbox|mine|unassigned|overdue|completed · `priority` LOW|NORMAL|HIGH|URGENT · `sort` createdAt|updatedAt|resolutionDueAt|priority · `order` asc|desc. Status keys: SUBMITTED, IN_PROGRESS, WAITING_FOR_EMPLOYEE, RESOLVED, CLOSED. Transition keys come only from `available_actions` in `get_hr_request` (empty until the request is assigned).
- Scripts reject unknown flags; if a call returns `unknown_args`, `*_must_be_uuid`, `version_required`, or `body_invalid`, fix the call once from the message — do not retry variants.

## App surface vs backend-only
- The app exposes: employee catalog/form/submission/detail/reply/attachments; HR inbox, request detail (assign, priority, due date, lifecycle buttons from `available_actions`, public reply, internal notes, internal attachments), reports (month filter only), request-type configuration (create, draft, publish, archive, restore, duplicate), app permissions.
- Backend-only (no app screen, do not describe as a button or menu): queue transfer, queue CRUD, privacy operations and legal holds. Offer them only when the user explicitly asks and is authorized.
- Files cannot be transferred through chat: for any upload, hand off to the app's uploader instead of inventing intent IDs.

## Safety and authorization
- Employee reads and writes are restricted by the service to the authenticated employee's tenant and requests.
- HR tools are intended for an authorized HR manager and remain subject to the service's ReBAC and tenant checks.
- Before any write tool, resolve identifiers, read the current version, show a parameter preview, and stop for explicit confirmation in a later turn. A request to preview, only check, or not send/save/upload yet means no write in that turn; a request to verify after a write means read only.
- After a backend validation error on a write, report it and ask the user; do not retry with altered payloads.
