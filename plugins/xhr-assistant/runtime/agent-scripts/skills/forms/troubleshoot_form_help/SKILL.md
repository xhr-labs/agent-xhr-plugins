---
name: forms-troubleshoot-form-help
description: Troubleshoot complex Forms setup, publishing, onboarding, review, public-link, workflow, submission, email, and compatibility issues in X-HR. Use when the user reports an error, missing action, wrong data, incomplete review, invalid link, or unexpected form behavior.
---

# Troubleshoot Forms Help

## Intent: forms-troubleshoot-form-help
### User request patterns
- troubleshoot a form setup problem
- find why a form cannot be published
- explain why a form action is missing
- fix a form that does not load
- diagnose missing onboarding fields
- troubleshoot a required onboarding form at login
- explain why an onboarding form is not forced at login
- troubleshoot a review form task
- explain why a public form link fails
- investigate missing form submissions
- diagnose incorrect submission values
- troubleshoot form email sending
- explain why a published form change is not live
- investigate legacy form fields

### Retrieval tags
- forms
- troubleshooting
- onboarding
- force-at-login
- blocking-onboarding
- review-form
- versions
- public-link
- task-hub
- submissions
- email
- compatibility
- direct-answer

### Answer objective
Provide a symptom-first troubleshooting path grounded in the current Forms frontend behavior, including category-specific and integration edge cases.

### Instructions
- Answer directly without calling executable tools.
- First identify the form category (General, Onboarding, Review), user role, entry point (Forms list, authenticated fill, Task Hub/Inbox, or public link), and status/version.
- Separate frontend behavior from backend ownership. Forms renders the Form Service presentation model; Workflow owns orchestration and Task Hub/Inbox owns task context.
- Never ask the user to expose a public token, password, employee data, raw IDs, or raw API payloads.
- Do not invent an **Unpublish** action. The current Forms frontend exposes share generation/regeneration, expiry, and password settings, but no standalone unpublish client method.
- Treat a successful mutation and a refreshed server response as the source of truth. Do not diagnose from stale list rows alone.
- When the issue involves live tenant data, give the diagnostic path but do not claim a specific form, version, submission, or permission exists without live data.

### Troubleshooting playbook

#### The Forms menu or page is missing

- The workspace Forms list is intended for Admin and HR Manager users. Employees may not see the menu.
- Employees normally complete forms through Task Hub, Inbox, an authenticated form route, or a public link.
- Open the Forms list from the supported [Forms]({{forms_url}}) destination; legacy workspace links may redirect there.
- If an Admin or HR Manager still cannot open the page, check session permissions, route access, and the list request rather than suggesting a different Forms URL.

#### A form cannot be saved or published

- Check that the form name is non-empty.
- General and Onboarding forms need at least one configured field unless this is a metadata-only edit.
- Every custom group needs a non-empty title.
- Review forms need at least one step and an assignee for every enabled step.
- Review steps without question fields trigger a warning. Sections, dividers, and text labels do not count as questions.
- Onboarding validation can fail because the catalog is loading, an attribute no longer exists, a mapped field type is incompatible, or a required group attribute is missing.
- Wait for a pending mutation to finish before retrying; the UI disables duplicate actions.

#### A published edit is not visible

- Normal published editing targets the latest editable draft. The live version remains unchanged until that draft is published.
- Submitted Data review is intentionally pinned to the active published version and is read-only.
- If no editable draft exists, the client creates one and retries version lookup. A race or delayed backend response can therefore require waiting for the operation to settle.
- Confirm that the draft was published successfully and refresh server-backed data before concluding that the change was lost.

#### Onboarding fields are missing or invalid

- Select the work location before loading employee attributes. The catalog is scoped by work location and country.
- Some groups allow partial selection, while locked groups still require every natively required attribute once that group is selected.
- Optional fields can be made required; natively required fields cannot be made optional.
- Contact address fields become dependent searchable selectors only when their metadata marks them as address components. Ordinary address lines remain text inputs.
- Bank selectors appear only for bank-option metadata; other bank fields remain text inputs.
- Dependents is a special onboarding group, may be unavailable for some countries, and can be added only once.
- Vietnam has special full-name and province/city/ward behavior. Do not diagnose it as a generic first/middle/last-name or free-text address issue.

#### A required onboarding form does not open at login

- **Force to show form on logging in** is a direct option in the Onboarding form's **Form setup** section. A separate workflow is not required for the login-blocking behavior.
- Confirm the checkbox was enabled, saved, and published. The setting is sent on onboarding create/update as `forceShowOnLogin`.
- The frontend shows the blocking dialog only when the authenticated session contains a `blockingOnboarding` projection with state `PRESENT` and a current task ID. If the checkbox is enabled but no dialog appears, the remaining investigation is the backend/WES task assignment and session projection, not another Forms route.
- The blocking dialog loads the onboarding task and its form version. Missing form/schema/version references can produce the required-form load error.
- The employee cannot dismiss a valid blocking dialog by clicking outside or pressing Escape. Retry, support, and logout are the available recovery paths when loading fails.
- After submission, the frontend completes the onboarding task and waits for the login projection to clear. A short synchronization delay can show a retry state even after the form was accepted.
- Use a workflow only when the requirement is event-based scheduling, recipient assignment, approval, or other orchestration beyond the direct login-blocking setting.

#### A review task is incomplete or shows the wrong fields

- Review forms are internal and should be completed through Workflow, Task Hub, or Inbox.
- The task-scoped form may contain only the assigned step plus permitted completed previous steps.
- Previous steps are read-only; only the assigned step is editable and submitted.
- If a task-scoped form has no `PUBLISHED` status, it may still be valid because Workflow already enforced task ownership and visibility.
- If a non-scoped form load returns 404, the runtime may fall back to the published Form Service form.
- Do not merge review rows in the frontend; grouped review/report structure comes from Form Service.

#### A public link does not open or submit

- A public link contains the form destination and a `#token=...` fragment; a missing fragment token produces an invalid link.
- Password-protected links require the configured password before the form is loaded.
- Expired or regenerated links may no longer be valid.
- The token is read from the URL fragment and sent in `X-Public-Form-Token`; the password is sent in `X-Public-Form-Password`.
- Public address and bank lookups use Form Service public proxy endpoints. They should not require an authenticated Employee Management request.
- Review and assigned-step forms may not expose public sharing.

#### Submissions are missing, blank, or grouped incorrectly

- Submitted Data is available for published forms and is pinned to the active published version.
- The table and detail view use backend-provided `renderType`, `columns`, `groups`, `rows`, and sections.
- Report/review details can intentionally show incomplete steps and an explicit not-done state.
- Column values use the exact backend `column.key`; do not assume mixed-case fallbacks.
- Submission detail is loaded on demand, so a list row can render while its detail request is still pending or can fail separately.
- PDF export is available for report-style details and is generated by the backend; the browser does not reconstruct the report.

#### Form email is unavailable or appears not to send

- Send via email is limited to published, public-share-eligible forms.
- It is unavailable for drafts, archived/deleted forms, Review forms, assigned-step forms, and forms with public sharing disabled.
- The flow resolves or creates a public link before sending, so link eligibility must be fixed first.
- Up to five supported attachments are accepted. Subject/body templates are locale-aware and fall back to English.
- Audit logs show the request as queued; queued status is not proof of final delivery.

#### An old or unusual field renders unexpectedly

- The frontend supports compatibility adapters for persisted legacy field types and unknown backend details are preserved during save.
- Text labels and section breaks are display-only and do not serialize answers.
- Matrix rating is stored using a compatibility `TEXT_LONG` representation with matrix configuration and answers serialized as JSON.
- Choice fields may source options from backend field options, config options, choices, or employee-attribute metadata.
- Unsafe, malformed, oversized, or catastrophic regex patterns are rejected by frontend safety checks.

### Escalation boundary

Escalate to backend/service investigation when the normalized response is missing required form data, version state conflicts after refresh, a public share remains valid contrary to policy, submission grouping is wrong in the returned presentation model, or an email remains queued beyond the supported delivery process. Include the form category, status, entry point, user-facing error, timestamp, and correlation information if available, but never include public tokens or passwords.
