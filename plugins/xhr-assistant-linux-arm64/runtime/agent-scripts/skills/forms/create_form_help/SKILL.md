---
name: forms-create-form-help
description: Explain how to create and configure a form in X-HR. Use when the user asks how to build a general form, add fields, groups, sections, steps, validation, or preview a form without requesting live form creation.
---

# Create Form Help

## Intent: forms-create-form-help
### User request patterns
- create a form in X-HR
- build a new employee form
- add fields and sections to a form
- configure required fields in a form
- preview a form before publishing

### Retrieval tags
- forms
- form-builder
- fields
- validation
- direct-answer

### Answer objective
Explain the current form-builder flow and the main configuration options.

### Instructions
- Answer directly without calling executable tools.
- Keep General, Onboarding, and Review forms separate. Ask which type the user means when the answer depends on the form category.
- Do not imply that creating a form automatically configures its workflow. Workflow assignment and task execution are related integrations handled by Workflow and Task Hub.

### Direct answer
1. Open [Forms]({{forms_url}}) and select **Add new form**.
2. Choose **General form**, **Onboarding form**, or **Review form**.
3. Enter the name, description, and work location when applicable.
4. Add fields from the builder toolkit. The standard picker includes text, long text, radio, checkbox, dropdown, matrix rating, email, full name, date, time, number, sections, and dividers.
5. Organize fields into groups or steps when the form needs sections or assigned stages.
6. Configure labels, options, validation, and required behavior, then use **Preview** to check the result.
7. Save and publish when the form is ready.

General forms need a name and at least one field. Grouped forms need a title for every group. Review forms need at least one step and an assignee for every enabled step; a warning appears when an enabled review step has no question fields. Section, divider, and text-label elements are layout content and do not collect answers.

For Onboarding forms, select the work location before choosing employee attributes. Available attributes and validation depend on the location and country. System-required onboarding attributes cannot be made optional.
