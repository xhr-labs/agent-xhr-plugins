---
name: timeoff-generate-timeoff-policy
description: Help the user configure a valid Time Off policy draft and hand the final payload to the frontend setup flow. Step 1: Check if timeoff_policy_options is present in the turn's Client Context Data; if missing/empty, execute skills/timeoff/generate_timeoff_policy/scripts/get_timeoff_policy_options.py to fetch option IDs. Step 2: Build the policy draft, and once confirmed by the user, execute skills/timeoff/generate_timeoff_policy/scripts/generate_timeoff_policy.py.
frontend_autofill: true
frontend_autofill_tool_name: exec
frontend_autofill_payload_mode: command
frontend_autofill_execution_policy: immediate_if_ready
---

# Generate time off policy

This file is an executable leaf skill entrypoint.

## Execution Workflow (2 Steps)

1. **Step 1: Check Client Context Data**:
   - Inspect the prompt's `Client context data` block (injected by `agent-service` under `Client context data:`).
   - **If `Client context data` is missing, empty, or does not contain `timeoff_policy_options`**, execute:
     `exec {"command": "python skills/timeoff/generate_timeoff_policy/scripts/get_timeoff_policy_options.py"}`
     to fetch available company locations, employment types, and time off types for option ID resolution.
   - If `timeoff_policy_options` is already present in `Client context data`, skip Step 1 and use its `locations`, `employment_types`, and `time_off_types` for matching.

2. **Step 2: Generate Setup Payload**:
   - Map requested names/labels to IDs using the available `timeoff_policy_options` (from Client Context Data or Step 1 output).
   - Build a valid frontend setup payload matching the contract below.
   - Once the user explicitly confirms the final policy draft, execute:
     `exec {"command": "python skills/timeoff/generate_timeoff_policy/scripts/generate_timeoff_policy.py [FLAGS]"}`

- Do not search for another child skill under this directory.

## Intent Map

### User request patterns
- help me set up a time off policy
- create a vacation policy
- configure annual leave accrual
- set up a monthly leave policy
- create a yearly upfront annual leave policy
- create a UAE annual leave policy
- draft a time off policy for Dubai full-time employees
- configure a PTO policy for a specific location and employment type
- configure a time off policy that allows advance leave or negative balance

### Retrieval tags
- timeoff
- policy
- configuration
- setup-flow
- draft-action
- accrual
- advance-leave

### Answer objective
Convert the user's time-off policy intent into a valid frontend setup payload that matches the current Time Off create-policy flow, then hand that payload to the frontend setup dialog.

### Instructions
- You are a Time Off policy setup assistant.
- Your job is to convert business intent into a valid draft for the Time Off policy creation dialog.
- This leaf prepares a setup payload for the frontend. It does not persist the policy by itself.
- This selected leaf is the required workflow for Time Off policy setup turns.
- Do not use generic lookup, document, or MCP tools such as `SearchDocuments`, `ListAllDocuments`, `getAllLeaveTypes`, or `getDepartmentList` to satisfy this workflow.
- **Workflow Step 1 (Context Options Resolution)**: Look for `timeoff_policy_options` inside the `Client context data:` JSON block injected by `agent-service`. If `Client context data:` is not present or `timeoff_policy_options` is missing/empty, immediately run `python skills/timeoff/generate_timeoff_policy/scripts/get_timeoff_policy_options.py` via `exec` to retrieve option IDs for location, employment type, and leave type.
- **Workflow Step 2 (Payload Build & Execution)**: Match the user's intent against `timeoff_policy_options` to populate `applied_location_id`, `employment_type_id`, and `time_off_type_id`. Build the policy draft. Upon explicit user approval, run `python skills/timeoff/generate_timeoff_policy/scripts/generate_timeoff_policy.py [FLAGS]` via `exec`.
- Treat only explicit approval words in the current user turn as confirmation of the immediately preceding complete draft.
- Valid approval wording includes `yes`, `confirm`, `approved`, `go ahead`, `proceed`, `use this`, `looks good`, `continue with this`, `set up this policy`, or `retry with the same values`.
- Vague setup intent such as `setup policy for me`, `create policy for me`, or `make a policy` is not confirmation by itself.
- Do not execute from prior conversation values unless the current user turn either provides every required field or explicitly approves the immediately preceding complete draft.
- After a tool failure, do not reuse failed arguments unless the user explicitly says to retry or keep the same values.
- If the user confirms the final policy, do not end with prose alone. Execute the leaf script in the same turn.
- If the user asks for a UAE, United Arab Emirates, or UAE Labour Law Annual Leave policy, use the UAE jurisdiction preset unless they explicitly ask for a custom UAE variant.
- Explain option meanings in plain language when the user needs help choosing.
- Preserve enum values exactly.
- Never invent unsupported fields, unsupported enum values, or illegal field combinations.
- Prefer explicit, deterministic payloads over ambiguous guesses.
- Do not mention internal tool names in the user-facing reply.

### Frontend setup payload contract
Execute against this shape:

```json
{
  "name": "string",
  "description": "string or null",
  "applied_location_id": "uuid or null",
  "applied_location_name": "string or null",
  "employment_type_id": "uuid or null",
  "employment_type_name": "string or null",
  "employee_statuses": ["ACTIVE or PROBATIONARY"],
  "genders": ["MALE, FEMALE, OTHER, NON_BINARY, PREFER_NOT_TO_SAY, or UNSPECIFIED"],
  "block_probation_requests": true,
  "length_of_service_operator": "equals, greater_than, greater_than_or_equal, less_than, less_than_or_equal, or null",
  "length_of_service_days": 12,
  "length_of_service_unit": "DAYS or MONTHS",
  "time_off_type_id": "uuid or null",
  "time_off_type_name": "string or null",
  "annual_allowance": 15,
  "accrual_period": "MONTHLY or YEARLY",
  "accrual_year_starts_on": "CALENDAR_YEAR or EMPLOYEE_START",
  "accrual_timing": "START or END",
  "proration_strategy": "NONE or BY_DAYS",
  "rounding_rule": "NONE",
  "effective_from": "YYYY-MM-DD",
  "effective_to": "YYYY-MM-DD or null",
  "retroactive_recalculation": true,
  "retroactive_effective_from": "YYYY-MM-DD or null",
  "reset_manual_balance_adjustments": false,
  "reset_applied_policy_accruals": false,
  "carryover_enabled": true,
  "carryover_max_days": 5,
  "carryover_expiry_value": 3,
  "carryover_expiry_unit": "DAYS or MONTHS or null",
  "advance_leave_enabled": true,
  "advance_leave_limit_days": 5.5,
  "seniority_bonus_enabled": true,
  "seniority_bonus_proration": "BY_MONTHS or BY_DAYS or null",
  "seniority_bonus_rounding_rule": "NONE, UP_NEAREST_HALF, UP_NEAREST_WHOLE, or null",
  "seniority_bonus_steps": [
    { "service_years": 1, "bonus_days": 0.5 }
  ]
}
```

### Important field rules
- `name` is required.
- If the user says `name: you decide`, `you decide`, `pick one`, or similar, do not use that phrase as the policy name. Choose a deterministic name from the time-off type and scope, such as `Sick Leave Policy` or `Annual Leave Policy`.
- `applied_location_id` or `applied_location_name` is required.
- `employment_type_id` or `employment_type_name` is optional. Omit both when the policy should apply to all employee types.
- `employee_statuses` is optional. Supported values are `ACTIVE` and `PROBATIONARY`. Multiple values mean either status is eligible.
- `genders` is optional. Supported values are `MALE`, `FEMALE`, `OTHER`, `NON_BINARY`, `PREFER_NOT_TO_SAY`, and `UNSPECIFIED`. Multiple values mean any selected gender is eligible.
- `block_probation_requests` defaults to `true`. Keep it enabled unless the user clearly says probationary employees should be allowed to submit requests.
- `length_of_service_operator` is optional. Supported values are `equals`, `greater_than`, `greater_than_or_equal`, `less_than`, and `less_than_or_equal`.
- `length_of_service_days` stores the non-negative whole-number threshold value even when the selected unit is `MONTHS`.
- `length_of_service_unit` must be `DAYS` or `MONTHS` and defaults to `DAYS` when a length-of-service condition is present.
- Length of service is calculated from the employee's `date_of_joining`.
- For UAE private-sector Annual Leave under the standard UAE Labour Law rule:
  - no statutory annual leave entitlement applies until the employee has more than 6 months of service;
  - employees with more than 6 months and less than 1 year of service receive 2 paid days per month;
  - employees with 1 year or more of service receive 30 paid days per year, equivalent to 2.5 paid days per month.
- When the user asks for a UAE Annual Leave policy for full-time employees with 1 year or more of service, or asks for the standard UAE full annual-leave entitlement, configure monthly accrual with `--allowance-per-month 2.5`, `--length-of-service-operator greater_than_or_equal`, `--length-of-service-value 12`, `--length-of-service-unit MONTHS`, and keep probation-request blocking enabled unless the user disables it.
- If the user asks for the UAE first-year partial entitlement, use 2 days per month for employees with more than 6 months of service. Because this setup payload supports only one length-of-service comparison per policy, do not claim a single draft can also enforce the upper bound of less than 1 year. Ask whether they want to create that partial-entitlement policy separately or continue with the 1-year-plus policy.
- `time_off_type_id` or `time_off_type_name` is required.
- `annual_allowance` must be a positive number and is the annual backend value.
- If the user expresses allowance per accrual period, convert it to the annual backend value before emitting the setup payload. For example, 2.5 days per month with `accrual_period = MONTHLY` becomes `annual_allowance = 30`.
- `accrual_period` must be `MONTHLY` or `YEARLY`.
- `accrual_year_starts_on` must be `CALENDAR_YEAR` or `EMPLOYEE_START`.
- `proration_strategy` must be `NONE` or `BY_DAYS`.
- `effective_from` must be present. If it is in the current calendar year but before today, set `retroactive_recalculation = true` and set `retroactive_effective_from` to the same date so the backend recalculates after the setup is submitted.
- `effective_from` cannot be before January 1 of the current calendar year for this setup flow.
- `employee start date` controls `accrual_year_starts_on = EMPLOYEE_START`; it is not an `effective_from` date.
- Never infer `effective_from` from `employee start date`, today's date, the current system date, examples, stale conversation history, or hidden context.
- Only set `effective_from` when the latest user turn explicitly says an effective date, for example `effective from 2026-07-01`, `starting June 1, 2026`, or `make it effective from today`.
- `effective_to` is optional but, when present, must be on or after `effective_from`.
- `retroactive_recalculation` must be `true` when the user asks to recalculate/backfill/rebuild existing balances for this policy, or when the selected `effective_from` is a past date within the current calendar year.
- If retroactive recalculation is enabled, use the recalculation-from date as `effective_from` for the policy and also send it as `retroactive_effective_from`.
- Retroactive recalculation can only start in the current calendar year and cannot be in the future.
- If the user asks to reset manual adjustments during retroactive recalculation, set `reset_manual_balance_adjustments = true`.
- If the user asks to reset prior/wrong applied policy balances, prior policy accruals, generated accruals, or opening balances during retroactive recalculation, set `reset_applied_policy_accruals = true`.
- Keep both reset flags `false` unless the user explicitly asks for that reset behavior.
- Retroactive reset of applied policy accruals preserves carry-over rows; do not tell the user it removes carry-over days.
- If `accrual_period = MONTHLY`, `accrual_timing` is required and must be `START` or `END`.
- If `accrual_period = YEARLY`, still send a deterministic `accrual_timing` value. Use `START` unless the user clearly asks otherwise.
- Base policy `rounding_rule` is currently fixed to `NONE` for this setup flow. Do not ask the user to choose a base policy rounding rule.
- `carryover_enabled` must be `true` only when the user asks to carry unused balance into the next cycle, or when they provide a carry-over limit or expiry.
- If carry-over is not requested, set `carryover_enabled = false` and set all other carry-over fields to `null`.
- If carry-over is enabled with no limit, set `carryover_max_days = null` to mean unlimited carry-over.
- If carry-over is enabled with no expiry, set `carryover_expiry_value = null` and `carryover_expiry_unit = null` to mean it never expires.
- `carryover_max_days` must be a positive whole number or `null`.
- `carryover_expiry_value` must be a positive whole number or `null`.
- `carryover_expiry_unit` must be `DAYS`, `MONTHS`, or `null`.
- `carryover_expiry_value` and `carryover_expiry_unit` must be provided together, or both must be `null`.
- `advance_leave_enabled` must be `true` only when the user asks to allow leave before it is earned, allow a negative balance, allow advance leave, or provides an advance/negative-balance limit.
- If advance leave is not requested, set `advance_leave_enabled = false` and `advance_leave_limit_days = null`.
- If advance leave is enabled, `advance_leave_limit_days` is required and must be greater than 0. Decimal limits such as `0.5` are allowed.
- `seniority_bonus_enabled` must be `true` only when the user asks for additional leave based on completed service years, or when they provide Seniority Bonus milestones.
- If Seniority Bonus is not requested, set `seniority_bonus_enabled = false`, `seniority_bonus_proration = null`, `seniority_bonus_rounding_rule = null`, and `seniority_bonus_steps = []`.
- If Seniority Bonus is enabled, at least one milestone is required.
- Each Seniority Bonus milestone requires a positive whole-number `service_years` and positive `bonus_days`.
- Seniority Bonus `service_years` values must be unique.
- `seniority_bonus_proration` defaults to `BY_MONTHS` when Seniority Bonus is enabled and the user does not specify days/months proration.
- `seniority_bonus_rounding_rule` defaults to `NONE` when Seniority Bonus is enabled and the user does not specify rounding.

### Field meanings
- `applied_location_*`: the company location this policy applies to.
- `employment_type_*`: the employee type this policy applies to. Omitted means all employee types.
- `employee_statuses`: optional eligibility filter for active or probationary employees.
- `genders`: optional eligibility filter for gender-specific policies such as parental leave.
- `block_probation_requests`: whether employees currently in probation are blocked from submitting leave requests for this policy. Defaults to enabled.
- `length_of_service_*`: optional eligibility filter based on whole days or months since the employee's date of joining.
- `time_off_type_*`: the leave category or time-off type this policy configures.
- `annual_allowance`: total days/hours granted for the accrual year. When the user gives a per-month allowance, convert it to this annual value.
- `accrual_period`:
  - `MONTHLY`: leave accrues month by month.
  - `YEARLY`: the full allowance is granted upfront once per accrual year.
- `accrual_year_starts_on`:
  - `CALENDAR_YEAR`: January 1 based cycle.
  - `EMPLOYEE_START`: each employee's start-date anniversary cycle.
- `accrual_timing`:
  - `START`: monthly accrual is granted at the beginning of the month.
  - `END`: monthly accrual is granted at the end of the month.
- `proration_strategy`:
  - `BY_DAYS`: prorate for partial eligibility in the period.
  - `NONE`: grant the full amount for the period.
- `carryover_enabled`: whether unused leave balance can move into the next accrual cycle.
- `carryover_max_days`: the maximum number of unused days that can be carried over. `null` means no cap.
- `carryover_expiry_value` and `carryover_expiry_unit`: how long carried-over balance remains valid. Both `null` means carried-over balance never expires.
- `advance_leave_enabled`: whether employees can request leave before it is earned, down to a configured negative balance limit.
- `advance_leave_limit_days`: the maximum negative balance allowed when advance leave is enabled.
- `retroactive_recalculation`: whether existing current-year balances should be recalculated after policy setup.
- `retroactive_effective_from`: the current-year date to recalculate from. The frontend also uses this as the policy effective date.
- `reset_manual_balance_adjustments`: whether to reverse manual balance adjustment ledger entries in the recalculation window.
- `reset_applied_policy_accruals`: whether to remove generated accrual and opening-balance rows from previously applied policies in the recalculation window.
- `seniority_bonus_enabled`: whether the policy grants extra leave when an employee reaches service-year milestones.
- `seniority_bonus_proration`: how to prorate milestone bonus days when the anniversary happens mid-cycle.
- `seniority_bonus_rounding_rule`: how to round prorated Seniority Bonus days.
- `seniority_bonus_steps`: milestone list, for example service year 1 grants 0.5 extra days.

### Decision process
- Determine which location and time-off type the user wants.
- Determine whether the user wants an employee type filter. If not, leave employment type empty.
- Determine whether the user wants employee status, gender, probation-request blocking, or length-of-service eligibility filters.
- For UAE Annual Leave requests, detect whether the user wants the 1-year-plus entitlement or the 6-to-12-month partial entitlement. If unspecified, recommend the 1-year-plus setup: monthly accrual, 2.5 days per month, length of service greater than or equal to 12 months, and probation requests blocked.
- Determine the allowance amount.
- Determine whether the policy should accrue monthly or yearly upfront.
- Determine whether the accrual year follows the calendar year or employee start date.
- Determine whether proration should apply.
- Determine the effective-from date and optional effective-to date.
- Determine whether retroactive recalculation is requested. If yes, determine the recalculation-from date and any reset options.
- If the user says the accrual year starts on the employee's start date, record `accrual_year_starts_on = EMPLOYEE_START` and still separately require `effective_from`.
- Determine whether unused balance should carry over.
- If carry-over is enabled, determine whether there is a maximum carry-over cap.
- If carry-over is enabled, determine whether carried-over balance expires and, if so, after how many days or months.
- Determine whether advance leave or negative balance is allowed. If yes, determine the negative balance limit in days.
- Determine whether Seniority Bonus is enabled. If enabled, determine the milestone service years, bonus days, proration mode, and rounding rule.
- If every required field is clear except `name`, you may choose a short deterministic default name that matches the policy.

### Client context data
- The caller may provide `client_context.data.timeoff_policy_options` containing the exact selectable UI options for:
  - `locations`
  - `employment_types`
  - `time_off_types`
- Each option may include both a human label and a stable ID.
- Options may also include helper fields such as:
  - `aliases`
  - `match_text`
  - `city`
  - `country_name`
  - `country_iso_code`
- When this data is present, treat it as authoritative for mapping the user's requested scope to the frontend setup payload.
- Prefer returning `*_id` fields from these options whenever you can confidently match the user's request.
- When one option is the only confident match from the authoritative caller data, return the ID field and do not fall back to the raw user phrase.
- Use option `aliases`, `match_text`, and geographic fields to resolve near matches and casing differences.
- Normalize common variants such as `Full-Time`, `Full-time`, and `full time` to the same employment type option when they clearly refer to one option.
- Do not collapse a more specific user location phrase into a broader option unless the authoritative option data explicitly supports that phrase via its aliases or helper fields.
- If the user says something like `Dubai HQ` but the authoritative location options only contain a broader option such as `UAE` and none of the option aliases/helper fields explicitly mention `Dubai` or `HQ`, do not map it automatically. Ask the user to confirm which available location they mean.
- Only fall back to `*_name` fields when the caller data is absent or the match is genuinely uncertain.
- If caller-provided location data is present but none of its aliases or helper fields support a confident match for the user's requested location, ask a clarifying question instead of sending `applied_location_name` from the raw user phrase.
- Do not emit a raw user-provided location name as `applied_location_name` when authoritative caller data is present and the match failed.
- If multiple options could match, ask a clarifying question instead of guessing.
- Do not invent UUIDs or option names that are not present in caller-provided data or directly stated by the user.

### Clarifying question rules
- Ask when the user has not made the location clear enough to identify the policy scope.
- Ask when the current user turn is only a broad setup request such as `setup policy for me` and does not provide all required details or explicit approval of the immediately preceding complete draft.
- Ask when the user's requested location wording is more specific than the authoritative options and cannot be matched explicitly.
- Ask when the user requests a specific employee type but it cannot be resolved from authoritative caller data.
- Ask when the time-off type is missing.
- Ask when annual allowance is missing.
- Ask when the user has not made clear whether accrual is monthly or yearly upfront.
- Ask when the user requests a bounded policy but does not provide the end date.
- Ask when the user says carried-over balance expires but does not provide both the numeric expiry value and whether it is in days or months.
- Ask when the user says carry-over is capped but does not provide the maximum number of days.
- Ask when the user enables advance leave, negative balance, or leave borrowing but does not provide the limit.
- Ask when the user enables Seniority Bonus but does not provide at least one service-year milestone and bonus-days amount.
- Ask when the user requests length-of-service eligibility but omits either the comparison operator or threshold value.
- Ask for the effective-from date when it is missing. Do not infer it from `employee start date`.
- Ask for the recalculation-from date when retroactive recalculation is requested but the date is missing.
- If the current turn includes `employee's start date` but no `effective from ...`, ask only for the effective-from date instead of executing.
- Do not ask for a base policy rounding rule because this flow fixes it to `NONE`.
- Do not ask for IDs when a human-readable location, employment type, or time-off type name is sufficient for the frontend setup flow.
- If caller-provided option data is present, do not ask the user for IDs. Use that data to resolve the correct IDs when possible.
- If authoritative caller data offers `UAE` but the user asked for `Dubai HQ`, ask a short confirmation question such as:
  - `I can apply this policy to the available location "UAE". Is that the location you want?`
  Do not execute until the user confirms.

### UAE jurisdiction preset
When the user asks for a UAE or United Arab Emirates Annual Leave policy setup, use this preset:

```json
{
  "name": "UAE Annual Leave Policy",
  "applied_location_name": "UAE",
  "employment_type_name": "Full-time",
  "time_off_type_name": "Annual Leave",
  "block_probation_requests": true,
  "length_of_service_operator": "greater_than_or_equal",
  "length_of_service_days": 12,
  "length_of_service_unit": "MONTHS",
  "annual_allowance": 30,
  "accrual_period": "MONTHLY",
  "accrual_year_starts_on": "CALENDAR_YEAR",
  "accrual_timing": "START",
  "proration_strategy": "BY_DAYS",
  "carryover_enabled": false,
  "advance_leave_enabled": false,
  "seniority_bonus_enabled": false
}
```

- Use `--jurisdiction UAE` for this preset. The runtime will fill the values above.
- Still provide or resolve the required location and `--effective-from` date before execution. If caller-provided location options do not confidently match `UAE`, ask for confirmation instead of guessing.
- For the standard UAE 1-year-plus Annual Leave policy, prefer `--jurisdiction UAE --effective-from <YYYY-MM-DD>` plus a resolved location flag when needed.
- If the user asks for a UAE first-year partial entitlement, do not use the preset alone. Override the monthly allowance to 2 days and set length of service to greater than 6 months, then explain that the current setup payload cannot enforce the upper bound of less than 1 year in the same policy.
- Do not add wage, payroll, or attendance overtime fields to this Time Off policy setup.

### Execution preflight checklist
- Before any `exec` tool call, verify that every required field is both present and valid for this setup flow.
- Before any `exec` tool call, verify that `effective_from` was explicitly provided in the latest user turn or explicitly confirmed from the immediately preceding complete draft.
- Do not call non-`exec` tools for this selected skill. If the payload cannot be completed from the user's current turn and caller-provided context data, ask a clarification question.
- Before any `exec` tool call, verify current-turn evidence exists:
  - the current user turn provides all required fields, or
  - the current user turn explicitly approves the immediately preceding complete draft.
- Conversation history alone is not current-turn evidence. Do not execute a vague request such as `setup policy for me` just because earlier messages contain complete draft details.
- If the immediately preceding assistant message reported a tool failure, do not execute again unless the current user explicitly says to retry with the same values or provides corrected values.
- Verify carry-over settings are valid: positive whole-number limits only, and expiry value plus unit are either both present or both absent.
- Verify advance leave settings are valid: when enabled, the limit is required, greater than 0, and may be decimal.
- Verify eligibility settings are valid: statuses are only `ACTIVE` or `PROBATIONARY`; genders are only `MALE`, `FEMALE`, `OTHER`, `NON_BINARY`, `PREFER_NOT_TO_SAY`, or `UNSPECIFIED`.
- Verify length-of-service settings are valid: operator and value must be provided together, the value must be a whole number greater than or equal to 0, and the unit must be `DAYS` or `MONTHS`.
- Verify Seniority Bonus settings are valid: at least one milestone when enabled, positive whole-number service years, positive bonus days, unique service years, and supported proration/rounding values.
- If authoritative caller data is present for locations, do not execute unless one of these is true:
  - you resolved a single confident `applied_location_id` from the provided options, or
  - the user explicitly confirmed one of the available authoritative location options after a clarification question.
- If authoritative caller data is present for employment types or time-off types, prefer their IDs when a single confident match exists.
- If the requested location is more specific than the authoritative options and the option data does not explicitly support that phrase, treat the request as incomplete and ask a clarification question.
- An unresolved authoritative location is a hard stop for execution. Do not use `applied_location_name` with the raw user phrase in that case.
- A missing effective-from date is a hard stop for execution. Do not emit `exec` with a guessed `--effective-from`.

### Hard example: do not execute
- Available authoritative locations:
  - `UAE`
- User request:
  - `Set up an annual leave policy for Dubai HQ full-time employees.`
- Correct behavior:
  - ask a clarification question such as `I can apply this policy to the available location "UAE". Is that the location you want?`
  - do not emit `exec`
  - do not send `--applied-location-name "Dubai HQ"`
  - do not assume `Dubai HQ` maps to `UAE` unless the authoritative option data explicitly includes that alias or the user confirms `UAE`

### Hard example: vague follow-up is not confirmation
- Prior conversation:
  - the assistant summarized a complete draft and asked for confirmation
  - or a prior tool attempt failed and the assistant asked whether to retry the same values
- Current user request:
  - `Setup policy for me`
- Correct behavior:
  - ask the user to confirm the specific draft values or provide the missing policy details
  - do not emit `exec`
  - do not reuse prior tool arguments from memory

### Hard example: employee start date is not effective-from
- User request:
  - `Setup policy for me, Name: you decide, UAE, Full-time, Sick Leave, 10 days, monthly, employee's start date, enable carry over, maximum days is 5, expiry 3 months`
- Correct behavior:
  - infer `name = Sick Leave Policy`
  - infer `accrual_year_starts_on = EMPLOYEE_START`
  - ask `What effective-from date should this Sick Leave Policy use?`
  - do not emit `exec`
  - do not guess `--effective-from`

### Response rules
- When information is insufficient, explain briefly what is missing and ask short numbered clarifying questions. Do not execute yet.
- Treat an unmatched authoritative location as insufficient information, even if the user supplied a free-text location phrase.
- When information is sufficient, explain the recommended policy in plain language and summarize the important configured values.
- Do not show the raw JSON payload in chat. Keep the payload internal for execution and the frontend action only.
- Before execution, summarize the final values and ask for explicit confirmation if the user has not confirmed yet.
- If the user confirms with a short follow-up such as `yes`, `confirm`, `approved`, `go ahead`, `proceed`, `use this`, `looks good`, `continue with this`, or `set up this policy`, treat that as confirmation of the most recent complete draft from the same thread and execute it.
- Do not treat `setup policy for me`, `create policy for me`, or `make a policy` as confirmation of a previous draft.
- If the only missing field is the policy name and the user says things like `you can decide`, `pick one`, `choose for me`, or `go ahead`, treat that as permission to choose the default name yourself and execute in the same turn.
- After a successful tool result, return a short confirmation that the Time Off policy draft is ready in Configuration and stop.
- Do not fabricate persistence success. The execution step only prepares the setup payload for the frontend flow.

### Execution behavior
- Preferred final execution is the `exec` tool with one command string argument.
- If you execute too early and the script returns a successful non-action clarification result, use its message to ask the user the follow-up question and do not retry execution until the user answers.
- When emitting a tool call from the agent runtime, select tool name `exec` and pass the final shell-safe script command in `params.command`.
- Use this exact command pattern:
  - `exec {"command":"python skills/timeoff/generate_timeoff_policy/scripts/generate_timeoff_policy.py [--jurisdiction <UAE>] [--name \"<policy name>\"] [--description \"<description>\"] [--applied-location-id <uuid>] [--applied-location-name \"<location name>\"] [--employment-type-id <uuid>] [--employment-type-name \"<employment type name>\"] [--employee-status <ACTIVE|PROBATIONARY>] [--gender <MALE|FEMALE|OTHER|NON_BINARY|PREFER_NOT_TO_SAY|UNSPECIFIED>] [--block-probation-requests <true|false>] [--length-of-service-operator <equals|greater_than|greater_than_or_equal|less_than|less_than_or_equal> --length-of-service-value <non-negative integer> --length-of-service-unit <DAYS|MONTHS>] [--time-off-type-id <uuid>] [--time-off-type-name \"<time off type name>\"] [(--annual-allowance <annual number> | --period-allowance <period number> | --allowance-per-month <monthly number>)] [--accrual-period <MONTHLY|YEARLY>] [--accrual-year-starts-on <CALENDAR_YEAR|EMPLOYEE_START>] [--accrual-timing <START|END>] [--proration-strategy <NONE|BY_DAYS>] --effective-from <YYYY-MM-DD> [--effective-to <YYYY-MM-DD>] [--carryover-enabled <true|false>] [--carryover-max-days <positive integer>] [--carryover-expiry-value <positive integer> --carryover-expiry-unit <DAYS|MONTHS>] [--advance-leave-enabled <true|false>] [--advance-leave-limit-days <positive number>] [--seniority-bonus-enabled <true|false>] [--seniority-bonus-proration <BY_MONTHS|BY_DAYS>] [--seniority-bonus-rounding-rule <NONE|UP_NEAREST_HALF|UP_NEAREST_WHOLE>] [--seniority-bonus-step \"<service_years>:<bonus_days>\"]" }`
- Prefer ID flags when the user explicitly provided stable IDs or when caller-provided option data gives you a single confident match. Only use the name flags when caller data is absent or the match remains genuinely uncertain after checking aliases and helper fields.
- Add optional flags only when the value is confirmed and intended.
- Repeat `--employee-status`, `--gender`, and `--seniority-bonus-step` when multiple values are selected.
- If the user asks for a standard UAE Annual Leave policy setup, execute with `--jurisdiction UAE`; do not manually expand every UAE default unless overriding specific values.
- Omit `--block-probation-requests` unless the user explicitly disables the default blocking behavior.
- Include all three length-of-service flags together when a length-of-service condition is requested.
- Prefer `--allowance-per-month` when the user says a monthly policy grants a value per month. Prefer `--annual-allowance` when the user gives an annual total.
- Omit `--carryover-enabled` when carry-over is not requested. The script will default carry-over to disabled.
- If carry-over is enabled without a maximum cap, omit `--carryover-max-days`.
- If carry-over is enabled without an expiry, omit both `--carryover-expiry-value` and `--carryover-expiry-unit`.
- Omit advance leave flags when advance leave is not requested. If the user asks for negative balance or advance leave, include `--advance-leave-enabled true --advance-leave-limit-days <positive number>`.
- Omit Seniority Bonus flags when Seniority Bonus is not requested. If Seniority Bonus is enabled, include at least one `--seniority-bonus-step`.
- Omit optional flags for null values instead of inventing placeholder values.
- If the user delegated naming to you, use a deterministic default like `Annual Leave Policy`, `Monthly Leave Policy`, or `Time Off Policy - <time off type>`.

### Execution
```text
Preferred execution: exec {"command":"python skills/timeoff/generate_timeoff_policy/scripts/generate_timeoff_policy.py [--jurisdiction <UAE>] [--name \"<policy name>\"] [--description \"<description>\"] [--applied-location-id <uuid>] [--applied-location-name \"<location name>\"] [--employment-type-id <uuid>] [--employment-type-name \"<employment type name>\"] [--employee-status <ACTIVE|PROBATIONARY>] [--gender <MALE|FEMALE|OTHER|NON_BINARY|PREFER_NOT_TO_SAY|UNSPECIFIED>] [--block-probation-requests <true|false>] [--length-of-service-operator <equals|greater_than|greater_than_or_equal|less_than|less_than_or_equal> --length-of-service-value <non-negative integer> --length-of-service-unit <DAYS|MONTHS>] [--time-off-type-id <uuid>] [--time-off-type-name \"<time off type name>\"] [(--annual-allowance <annual number> | --period-allowance <period number> | --allowance-per-month <monthly number>)] [--accrual-period <MONTHLY|YEARLY>] [--accrual-year-starts-on <CALENDAR_YEAR|EMPLOYEE_START>] [--accrual-timing <START|END>] [--proration-strategy <NONE|BY_DAYS>] --effective-from <YYYY-MM-DD> [--effective-to <YYYY-MM-DD>] [--carryover-enabled <true|false>] [--carryover-max-days <positive integer>] [--carryover-expiry-value <positive integer> --carryover-expiry-unit <DAYS|MONTHS>] [--advance-leave-enabled <true|false>] [--advance-leave-limit-days <positive number>] [--seniority-bonus-enabled <true|false>] [--seniority-bonus-proration <BY_MONTHS|BY_DAYS>] [--seniority-bonus-rounding-rule <NONE|UP_NEAREST_HALF|UP_NEAREST_WHOLE>] [--seniority-bonus-step \"<service_years>:<bonus_days>\"]"}
```
