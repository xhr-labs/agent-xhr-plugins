---
name: allocation-management-setup-help
description: Explain how HR or Admin sets up Allocation Management, including its five employee and department custom fields, employee values, data refresh, capacity prerequisites, permissions, and setup troubleshooting.
---

# Allocation Management Setup Help

## Intent: allocation-management-setup-help
### User request patterns
- set up Allocation Management
- explain the custom fields required by Allocation Management
- configure FTE, CAP, and PROD for Allocation Management
- configure the SOURCE field for Allocation Management
- make employees appear in the Allocation employee picker
- fix an employee FTE or capacity setup error
- refresh Allocation Management after changing employee custom fields
- check whether Allocation Management setup is complete
- explain whether a Roster setup is needed for Allocation Management

### Retrieval tags
- allocation-management
- allocation-setup
- custom-fields
- FTE
- CAP
- PROD
- SOURCE
- employee-capacity
- data-refresh
- troubleshooting
- direct-answer

### Answer objective
Give HR or Admin a complete, implementation-accurate Allocation Management setup runbook and explain the symptoms of incomplete or stale setup.

### Instructions
- Answer directly in text using the runbook below.
- Do not call executable tools for this skill.
- Start with the five custom fields, where to add them, and the exact names and codes to use.
- Explain that the fields are configured in X-HR employee and department profile forms; FTE, CAP, and PROD are employee fields, while SOURCE is a department field. Allocation Management reads their values; it does not populate them.
- Keep the two `FTE` fields distinct: Job Details FTE is an employee-level override, while Employee Type FTE is the fallback default.
- Recommend Text for both FTE fields, Boolean for `CAP` and `PROD`, and Text or Select for Department `SOURCE` depending on the available custom-field form. The SOURCE value must be one consistent reporting label. Do not recommend a numeric FTE field because the platform custom-field UI does not provide a numeric type.
- Explain the practical effect of blank values: employees without the right eligibility or capacity settings may not appear or may not be available for allocation, and missing FTE results in no usable capacity.
- Explain that Department `SOURCE` is needed for Source Line and own-line or cross-line reports, but it does not decide whether an employee can be allocated.
- Explain that Allocation prepares employee data after installation. If the app was installed before the fields or values were configured, ask an Admin to refresh Allocation data after completing setup.
- Mention that core monthly allocation does not require YouTrack, Workbench, or Attendance integrations. Those integrations are for optional project or timesheet workflows.
- Mention work-location working days, public-holiday calendars, and approved unpaid or maternity leave only as capacity-calculation prerequisites.
- Do not introduce Roster as an Allocation prerequisite. Roster is relevant to Attendance workflows; Allocation uses employee profile data, work-location calendars, and approved leave for capacity calculations.
- When troubleshooting, identify the likely missing field or unrefreshed Allocation data from the observed error. Do not claim that creating a field definition alone populates employee values.
- Keep allocation percentages above 0 and no higher than 100.

### Direct answer
#### Prerequisites

- An Admin or Workspace user must install or uninstall Allocation Management.
- An Admin user must create or edit the five custom fields in the employee and department profile configuration.
- HR/Admin should decide which employees are production and capacity-counted before populating `PROD` and `CAP`.

Open [Allocation Management]({{allocation_url}}) and the employee/department custom-field configuration.

#### 1. Create the five fields

Create each field as active. Use the exact names and field codes below, preferably in uppercase.

| Field code | Source and section | Type | Value or choices | How Allocation uses it |
| --- | --- | --- | --- | --- |
| `FTE` | Employee Profile -> Job Details | Text | A decimal such as `1`, `0.5`, or `0.75` | Employee-level FTE override |
| `CAP` | Employee Profile -> Job Details | Boolean | `true` for capacity-counted employees; `false` otherwise | Allows capacity calculation and allocation validation |
| `PROD` | Employee Profile -> Job Details | Boolean | `true` for employees eligible for Allocation; `false` otherwise | Controls whether the employee appears in Allocation selection |
| `FTE` | Employee Type -> Employee Type | Text | A decimal default such as `1` or `0.5` | Fallback FTE for employees of this type |
| `SOURCE` | Department -> Department | Text or Select | One consistent company Source Line label | Powers Source Line and line comparison reports |

The two `FTE` fields can use the same code because they are added in different areas. Do not create both fields in the same area.

For the `SOURCE` field, use the choices or text labels used by the company's reporting structure. The application does not define a universal list of Source Line names. Use consistent spelling and capitalization across departments.

Recommended requirement settings:

- Employee Type `FTE`: required.
- Employee Job Details `FTE`: optional, because it overrides the Employee Type default only when needed.
- `CAP`: required.
- `PROD`: required.
- Department `SOURCE`: required when Source Line reporting is used; optional if the company does not use line reporting.

#### 2. Populate the values

- Set a valid Employee Type `FTE` for every employee type that participates in planning.
- Set each employee's Job Details `CAP` to `true` when the employee should count toward capacity and be allowed in an allocation.
- Set each employee's Job Details `PROD` to `true` when the employee is allocation-applicable. Set it to `false` for non-production, business, or other excluded populations.
- Set Job Details `FTE` only when an employee's FTE differs from the standard for their employee type, such as for a part-time employee. Otherwise, leave it blank and the employee type default applies. The order is employee Job Details FTE, then Employee Type FTE, then no usable capacity when neither is valid.
- Set Department `SOURCE` for every department that should appear in Source Line reports.

#### 3. Prepare capacity inputs

For useful man-day and man-month calculations:

- Assign active employees to the correct work location.
- Configure working days for each work location.
- Configure public-holiday calendars where applicable.
- Keep approved unpaid and maternity leave requests in Timeoff so capacity reductions are reflected.

These settings affect capacity calculations; they do not replace the five Allocation custom fields.

#### 4. Install and verify

Install Allocation Management from the [App Store]({{app_store_url}}). After installation, Allocation prepares employee data for use. If the app was installed before the fields or values were configured, ask an Admin to refresh Allocation data after completing the setup. Creating a field definition alone does not set values for employees, employee types, or departments.

Verify the setup by checking that:

1. An active production employee with a positive resolved FTE and capacity tracking enabled appears in the Allocation employee picker.
2. The allocation preview shows the expected FTE value.
3. A valid active project can accept an allocation.
4. Source Line reports show the department's `SOURCE` value.

Core monthly allocation does not require YouTrack, Workbench, or Attendance integrations. Configure those only when the company needs project synchronization or planned-versus-actual timesheet reporting.

#### Common setup errors

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Employee does not appear in the picker | The employee is inactive, not production-enabled, has no valid FTE, or Allocation data is stale | Correct the employee state and values, then refresh Allocation data |
| Employee is not applicable for allocation | Employee is inactive or has `PROD` missing/false | Correct the employee state or `PROD` value, then refresh Allocation data |
| FTE must be greater than zero | FTE is missing or zero | Enter the employee's FTE or a default FTE for their employee type |
| Employee is excluded from capacity calculation | `CAP` is missing or false | Set `CAP = true` for employees who should be capacity-counted |
| Source Line is blank or unassigned | The department has no usable `SOURCE` value, or data is stale | Set the department's Source Line value and refresh Allocation data |
| New field exists but Allocation does not change | The field was created without values, or Allocation has not received the latest updates | Populate the values and refresh Allocation data |
| Allocation percentage is rejected | The percentage is outside the allowed range | Use a value above 0 and no higher than 100 |

Project role, YouTrack, Workbench, Attendance, and timesheet configuration are optional for the basic monthly allocation workflow. Allocation still requires a valid active project, employee permissions, and an unlocked allocation month.
