---
name: forms-onboarding-form-help
description: Explain how to configure and use employee onboarding forms in X-HR. Use when the user asks about onboarding attributes, bank or address fields, compliance fields, dependents, required toggles, forcing a form at login, public onboarding submissions, or creating employees from submitted onboarding data.
---

# Onboarding Form Help

## Intent: forms-onboarding-form-help
### User request patterns
- create an employee onboarding form
- add employee profile fields to onboarding
- collect bank address or compliance data during onboarding
- collect dependents in an onboarding form
- make optional onboarding fields required
- force an onboarding form to open at login
- require an onboarding form before platform access
- add an employee from an onboarding submission

### Retrieval tags
- forms
- onboarding
- employee-attributes
- dependents
- required-fields
- force-at-login
- blocking-onboarding
- direct-answer

### Answer objective
Explain work-location-aware onboarding forms and their employee-creation handoff.

### Instructions
- Answer directly without calling executable tools.
- Mention that available attributes can vary by work location and country.
- Distinguish employee-attribute fields from ordinary helper fields.
- Treat system-required attributes and country-specific catalogs as authoritative; do not suggest bypassing those validations.
- For login-blocking onboarding, explain the direct form setting before suggesting a workflow. A workflow is a separate option for event-based or assigned task orchestration.

### Direct answer
1. Open [Forms]({{forms_url}}), add a new form, and choose **Onboarding form**.
2. Select the work location before adding employee attributes so X-HR can load the correct employee, bank, address, and compliance catalog.
3. To require the form when an employee logs in, enable **Force to show form on logging in** in the **Form setup** section. This option is available for onboarding forms and is the direct setting for login-blocking onboarding.
4. Add complete attribute groups or selected fields, then arrange their order.
5. Optional onboarding fields can be made required individually or by group. Fields required by the system remain required.
6. Add the repeatable **Dependents** section when it is available for the selected country. It may be unavailable in countries where the product hides dependent tax-profile management.
7. Publish the form. Use a public link for external collection, a workflow task for event-based assignment, or the login setting above when the employee must complete the required onboarding task before entering the platform.
8. HR can review an unlinked public onboarding submission and use **Add employee** to prefill recognized profile data. Approved workflow onboarding data can also be written back to the employee profile.

When the login setting is enabled, it is saved as the form's `forceShowOnLogin` setting. On sign-in, when the backend provides a matching required onboarding task in the session, X-HR opens a blocking form dialog before the normal platform content. The employee can submit the form, log out, or contact support, but cannot dismiss the dialog or continue into the platform until the task is accepted.

Common setup failures usually mean the catalog is still loading, a required attribute was omitted, a mapped field type is incompatible, or the selected location/country does not match the intended employee profile.
