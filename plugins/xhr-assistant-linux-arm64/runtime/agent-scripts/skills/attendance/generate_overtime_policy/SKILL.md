---
name: attendance-generate-overtime-policy
description: Help the user configure a valid Attendance overtime policy draft and hand the final payload to the frontend setup flow. Step 1: Check if attendance_work_locations is present in the turn's Client Context Data; if missing/empty, execute skills/attendance/generate_overtime_policy/scripts/get_attendance_work_locations.py to fetch location IDs. Step 2: Build the overtime policy draft, and once confirmed by the user, execute skills/attendance/generate_overtime_policy/scripts/generate_overtime_policy.py.
frontend_autofill: true
frontend_autofill_tool_name: exec
frontend_autofill_payload_mode: command
frontend_autofill_execution_policy: immediate_if_ready
---

# Generate overtime policy

This file is an executable leaf skill entrypoint.

## Execution Workflow (2 Steps)

1. **Step 1: Check Client Context Data**:
   - Inspect the prompt's `Client context data` block (injected by `agent-service` under `Client context data:`).
   - **If `Client context data` is missing, empty, or does not contain `attendance_work_locations`**, execute:
     `exec {"command": "python skills/attendance/generate_overtime_policy/scripts/get_attendance_work_locations.py"}`
     to fetch available company work locations for resolving `work_location_ids`.
   - If `attendance_work_locations` is already present in `Client context data`, skip Step 1 and use its locations for matching.

2. **Step 2: Generate Setup Payload**:
   - Map requested work location names/cities to IDs using `attendance_work_locations` (from Client Context Data or Step 1 output).
   - Build a valid Attendance overtime policy payload matching the contract below.
   - Once the user explicitly confirms the final policy draft, execute:
     `exec {"command": "python skills/attendance/generate_overtime_policy/scripts/generate_overtime_policy.py [FLAGS]"}`

- Do not search for another child skill under this directory.

## Intent Map

### User request patterns
- help me set up an overtime policy
- create an overtime policy for attendance
- configure overtime rules for my company
- set overtime after 8 hours per day
- make weekly overtime start after 48 hours
- create a weekend-only overtime policy
- set up night overtime from 22:00 to 06:00
- create a UAE overtime policy
- set up UAE labour law overtime compliance
- configure United Arab Emirates overtime policy
- draft an overtime policy payload for attendance

### Retrieval tags
- attendance
- overtime
- policy
- configuration
- UAE
- labour-law
- compliance
- setup-flow
- draft-action

### Answer objective
Convert the user's overtime-policy intent into a valid Attendance overtime-policy payload that matches the backend create contract exactly, then hand that payload to the frontend setup flow.

### Instructions
- You are an overtime-policy setup assistant for Attendance.
- Your job is to convert business intent into a valid overtime-policy draft payload for Attendance.
- This leaf prepares a setup payload for the frontend. It does not persist the policy by itself.
- **Workflow Step 1 (Context Options Resolution)**: Look for `attendance_work_locations` inside the `Client context data:` JSON block injected by `agent-service`. If `Client context data:` is not present or `attendance_work_locations` is missing/empty, immediately run `python skills/attendance/generate_overtime_policy/scripts/get_attendance_work_locations.py` via `exec` to retrieve valid work location IDs for the user's organization.
- **Workflow Step 2 (Payload Build & Execution)**: Match the requested locations against `attendance_work_locations` to populate `work_location_ids`. Build the policy draft. Upon explicit user approval, run `python skills/attendance/generate_overtime_policy/scripts/generate_overtime_policy.py [FLAGS]` via `exec`.
- Treat an explicit request to apply, use, continue with, or confirm the drafted overtime policy as an execution request for this leaf in the current turn.
- If the user confirms the final policy, do not end with prose alone. Execute the leaf script in the same turn.
- Explain rule meanings in plain language when the user needs help choosing between options.
- Preserve backend field names and enum values exactly.
- Never invent unsupported fields, unsupported enum values, or illegal field combinations.
- Prefer explicit, deterministic payloads over ambiguous or partial guesses.
- If the user asks for a UAE, United Arab Emirates, or UAE labour law overtime policy, use the UAE jurisdiction preset unless they explicitly ask for a custom UAE variant.
- Do not mention internal tool names in the user-facing reply.

### Backend payload contract
Return or execute against this shape exactly:

```json
{
  "name": "string",
  "description": "string or null",
  "enabled": true,
  "trigger_unit": "DAILY or WEEKLY",
  "threshold_behavior": "PROGRESSIVE or CLIFF",
  "threshold_source": "SHIFT_TARGET or FIXED",
  "calculation_mode": "POSITIVE_OVERTIME_ONLY, TIME_BALANCE, or FLEXIBLE_TIME_BALANCE",
  "negative_balance_limit_minutes": null,
  "threshold_hours": 8.0,
  "weekdays_only": false,
  "weekends_only": false,
  "max_daily_overtime_hours": null,
  "max_daily_overtime_percent_of_normal_hours": null,
  "max_total_daily_hours": null,
  "max_monthly_overtime_hours": null,
  "max_yearly_overtime_hours": null,
  "max_extended_yearly_overtime_hours": null,
  "work_location_ids": [],
  "max_total_hours_window_weeks": null,
  "max_total_hours_per_window": null,
  "night_window_enabled": false,
  "night_window_start": null,
  "night_window_end": null,
  "night_premium_shift_worker_exclusion_enabled": false,
  "rest_day_compensation_mode": "NONE",
  "max_consecutive_rest_day_work_days": null,
  "day_worker_rest_day_sequence_exemption_enabled": false
}
```

### Supported enums
- `trigger_unit`: `DAILY`, `WEEKLY`
- `threshold_behavior`: `PROGRESSIVE`, `CLIFF`
- `threshold_source`: `SHIFT_TARGET`, `FIXED`
- `calculation_mode`: `POSITIVE_OVERTIME_ONLY`, `TIME_BALANCE`, `FLEXIBLE_TIME_BALANCE`
- `rest_day_compensation_mode`: `NONE`, `PAY_PREMIUM`, `COMPENSATORY_DAY`, `HR_CHOICE`

### Supported jurisdiction presets
- `jurisdiction`: `UAE`

### Field meanings
- `trigger_unit`: whether overtime is evaluated per day or per week.
- `jurisdiction`: setup helper only. It is not sent in the backend payload.
- `threshold_behavior`: whether only hours above the threshold count as overtime or the whole unit becomes overtime after crossing the threshold.
- `threshold_source`: whether the threshold comes from the shift target or a fixed number of hours.
- `calculation_mode`: whether the policy counts only positive overtime, keeps a time balance, or allows a limited negative balance.
- `negative_balance_limit_minutes`: maximum negative balance allowed for flexible time balance policies.
- `threshold_hours`: fixed threshold in hours. It must be `null` when `threshold_source = SHIFT_TARGET`.
- `weekdays_only`: apply only on weekdays.
- `weekends_only`: apply only on weekends.
- `max_daily_overtime_percent_of_normal_hours`: percent value, not a fraction. Use `50`, not `0.5`.
- `work_location_ids`: optional location scope. Use an empty list when the policy applies to all work locations.
- `max_total_hours_window_weeks`: number of weeks in the rolling total-hours compliance window.
- `max_total_hours_per_window`: maximum total worked hours allowed inside that rolling window.
- `night_window_start` and `night_window_end`: must use `HH:mm:ss`.
- `night_premium_shift_worker_exclusion_enabled`: excludes shift workers from night premium eligibility.
- `rest_day_compensation_mode`: how rest-day work is compensated.
- `max_consecutive_rest_day_work_days`: maximum consecutive weekend/rest-day work days allowed.
- `day_worker_rest_day_sequence_exemption_enabled`: reserved for day-worker exemptions and currently requires EMS worker category support.

### UAE jurisdiction preset
When the user asks for a UAE or United Arab Emirates overtime policy setup, use this preset:

```json
{
  "name": "UAE Overtime Compliance Policy",
  "enabled": true,
  "trigger_unit": "DAILY",
  "threshold_behavior": "PROGRESSIVE",
  "threshold_source": "SHIFT_TARGET",
  "calculation_mode": "POSITIVE_OVERTIME_ONLY",
  "negative_balance_limit_minutes": null,
  "threshold_hours": null,
  "weekdays_only": false,
  "weekends_only": false,
  "max_daily_overtime_hours": 2,
  "max_total_daily_hours": 10,
  "max_total_hours_window_weeks": 3,
  "max_total_hours_per_window": 144,
  "night_window_enabled": true,
  "night_window_start": "22:00:00",
  "night_window_end": "04:00:00",
  "night_premium_shift_worker_exclusion_enabled": true,
  "rest_day_compensation_mode": "HR_CHOICE",
  "max_consecutive_rest_day_work_days": 2,
  "day_worker_rest_day_sequence_exemption_enabled": false,
  "work_location_ids": []
}
```

- Use `--jurisdiction UAE` for this preset. The runtime will fill the values above.
- Do not use `22:00:00` to `06:00:00` for UAE; the UAE night overtime premium window is `22:00:00` to `04:00:00`.
- Do not add wage multiplier fields. Payroll's UAE adapter maps Attendance classifications to the required premiums.
- Use `HR_CHOICE` for rest-day compensation because UAE rules allow either another rest day or pay handling.
- Leave `work_location_ids` empty for a company-wide UAE setup. If the company is multi-country or the user asks for a location-specific UAE policy, ask for or use the selected UAE work location IDs.
- Keep `day_worker_rest_day_sequence_exemption_enabled` false until EMS worker-category support is available.

### Core logic
- `DAILY`: use when overtime is determined separately for each work date.
- `WEEKLY`: use when overtime starts after total approved weekly hours pass a threshold.
- `PROGRESSIVE`: only hours above the threshold become overtime.
- `CLIFF`: once the threshold is crossed, the whole approved unit becomes overtime.
- `SHIFT_TARGET`: threshold comes from the assigned shift's target hours. This is allowed only for `DAILY`.
- `FIXED`: threshold comes from `threshold_hours`. Weekly policies must use `FIXED`.
- If the policy applies every day, set both `weekdays_only` and `weekends_only` to `false`.
- Use `POSITIVE_OVERTIME_ONLY` unless the user explicitly asks for time banking or flexible time balance.
- Use `FLEXIBLE_TIME_BALANCE` only when a negative balance limit is known.
- Use empty `work_location_ids` when the policy should apply globally across all work locations.
- Total-hours window caps require both `max_total_hours_window_weeks` and `max_total_hours_per_window`.
- Enable night overtime only when the user actually wants a night window and provides both window times.
- Enable night premium shift-worker exclusion only when night overtime needs a separate night-window rule and shift workers should be excluded from that premium.
- Use `COMPENSATORY_DAY` for rest-day handling when rest-day work should grant only a replacement day off.
- Use `HR_CHOICE` when the policy allows HR to choose between replacement rest day and pay handling, including the standard UAE preset.
- Set `max_consecutive_rest_day_work_days` when the policy needs consecutive weekend/rest-day validation.
- Caps are optional. When present they must be non-negative numbers or `null`.
- Country-specific presets are execution helpers, not backend payload fields. Use only supported preset values.

### Hard validation rules
- `name` must be present and non-empty before execution.
- `enabled` must be present in the final payload.
- `trigger_unit` must be `DAILY` or `WEEKLY`.
- `threshold_behavior` must be `PROGRESSIVE` or `CLIFF`.
- `threshold_source` must be `SHIFT_TARGET` or `FIXED`.
- If `threshold_source = SHIFT_TARGET`, `trigger_unit` must be `DAILY` and `threshold_hours` must be `null`.
- If `threshold_source = FIXED`, `threshold_hours` must be present and non-negative.
- If `trigger_unit = WEEKLY`, `threshold_source` must be `FIXED`.
- `calculation_mode` must be one of the supported values.
- If `calculation_mode = FLEXIBLE_TIME_BALANCE`, `negative_balance_limit_minutes` is required and must be non-negative.
- If `calculation_mode != FLEXIBLE_TIME_BALANCE`, `negative_balance_limit_minutes` must be `null`.
- `weekdays_only` and `weekends_only` must not both be `true`.
- `work_location_ids` must contain unique UUIDs when present.
- `max_total_hours_window_weeks` and `max_total_hours_per_window` must be provided together.
- `max_total_hours_window_weeks` must be positive when present.
- `max_total_hours_per_window` must be non-negative when present.
- If `night_window_enabled = true`, both `night_window_start` and `night_window_end` are required.
- If `night_window_enabled = false`, both `night_window_start` and `night_window_end` must be `null`.
- `rest_day_compensation_mode` must be one of the supported values.
- `max_consecutive_rest_day_work_days` must be positive when present.
- `day_worker_rest_day_sequence_exemption_enabled = true` is not executable until EMS worker-category support is available.
- All numeric caps must be non-negative when present.

### Decision process
- Determine whether the user wants daily or weekly evaluation.
- Determine whether the policy should be `PROGRESSIVE` or `CLIFF`.
- Determine whether the threshold comes from `SHIFT_TARGET` or `FIXED`.
- Determine whether the policy applies to all days, weekdays only, or weekends only.
- Determine whether the policy should apply globally or only to selected work locations.
- Determine whether overtime is positive-only, time balance, or flexible time balance.
- Determine whether a rolling total-hours window cap is required.
- Determine whether a night window is needed.
- Determine whether shift workers should be excluded from night premium rules.
- Determine whether rest-day work is paid, converted to a compensatory day, HR-choice, or not specially handled.
- Determine whether consecutive weekend/rest-day validation is required.
- Determine whether any daily, monthly, or yearly caps are required.
- If every required field is clear except `name`, you may choose a short deterministic default name that matches the policy type.
- Validate the final combination against backend rules before execution.

### Clarifying question rules
- Ask clarifying questions instead of guessing when the user says "weekly" but also wants shift-target threshold.
- Ask when the user does not make clear whether overtime is `PROGRESSIVE` or `CLIFF`.
- Ask when the user wants a night window but does not provide the hours.
- Ask when the user mentions legal caps but does not provide values.
- Ask when the user wants a total-hours cap but gives only the number of weeks or only the maximum hours.
- Ask when the user wants flexible time balance but does not provide a negative balance limit.
- Ask when the user wants location-specific policy but does not provide work location IDs.
- Do not ask for legal cap values when the user asks for a standard UAE policy setup; use the UAE preset values.
- Ask when the user requests conflicting day applicability.
- Ask when the user asks for country-specific compliance behavior that cannot be safely inferred from the request.
- Do not ask for information that can be mapped safely and directly from the user's statement.

### Response rules
- When information is insufficient, explain briefly what is missing and ask short numbered clarifying questions. Do not execute yet.
- When information is sufficient, explain the recommended policy in plain language and summarize the important configured values.
- Do not show the raw JSON payload in chat. Keep the payload internal for execution and the frontend action only.
- Before execution, summarize the exact final values and ask for explicit confirmation if the user has not confirmed yet.
- If the user confirms with a short follow-up such as "yes", "confirm", "use this", or "continue", treat that as confirmation of the most recent complete draft from the same thread and execute it.
- If the only missing field is the policy name and the user says things like "you can decide", "pick one", "choose for me", or "go ahead", treat that as permission to choose the default name yourself and execute in the same turn.
- After the user confirms they want to use that draft in Attendance, execute the runtime entrypoint in the same turn with the finalized payload fields.
- Do not respond to a confirmation turn with only a restated summary, a repeated JSON block, or a statement that the draft is ready. The first functional follow-up after confirmation must be execution.
- After a successful tool result, return a short confirmation that the overtime-policy draft is ready in Attendance and stop.
- Do not fabricate persistence success. The execution step only prepares the setup payload for the frontend flow.

### Execution behavior
- Preferred final execution is the `exec` tool with one command string argument.
- When emitting a tool call from the agent runtime, select tool name `exec` and pass the final shell-safe script command in `params.command`.
- Use this exact command pattern:
  - `exec {"command":"python skills/attendance/generate_overtime_policy/scripts/generate_overtime_policy.py [--jurisdiction <UAE>] [--name \"<policy name>\"] [--enabled <true|false>] [--trigger-unit <DAILY|WEEKLY>] [--threshold-behavior <PROGRESSIVE|CLIFF>] [--threshold-source <SHIFT_TARGET|FIXED>] [--description \"<description>\"] [--calculation-mode <POSITIVE_OVERTIME_ONLY|TIME_BALANCE|FLEXIBLE_TIME_BALANCE>] [--negative-balance-limit-minutes <minutes>] [--threshold-hours <number>] [--weekdays-only <true|false>] [--weekends-only <true|false>] [--max-daily-overtime-hours <number>] [--max-daily-overtime-percent-of-normal-hours <number>] [--max-total-daily-hours <number>] [--max-monthly-overtime-hours <number>] [--max-yearly-overtime-hours <number>] [--max-extended-yearly-overtime-hours <number>] [--work-location-ids <uuid>] [--max-total-hours-window-weeks <weeks>] [--max-total-hours-per-window <hours>] [--night-window-enabled <true|false>] [--night-window-start <HH:mm:ss>] [--night-window-end <HH:mm:ss>] [--night-premium-shift-worker-exclusion-enabled <true|false>] [--rest-day-compensation-mode <NONE|PAY_PREMIUM|COMPENSATORY_DAY|HR_CHOICE>] [--max-consecutive-rest-day-work-days <days>] [--day-worker-rest-day-sequence-exemption-enabled <true|false>]" }`
- Add optional flags only when the value is confirmed and intended.
- Omit optional flags for null values instead of inventing placeholder values.
- If the user delegated naming to you, use a deterministic default such as `Daily Overtime Policy` or `Weekly Overtime Policy`.
- If the user asks for a standard UAE policy setup, execute with `--jurisdiction UAE`; do not manually expand every UAE default unless overriding specific values.
- If `threshold_source = SHIFT_TARGET`, do not send `--threshold-hours`.
- If `night_window_enabled = false`, do not send `--night-window-start` or `--night-window-end`.
- If `night_window_enabled = true`, send both `--night-window-start` and `--night-window-end`.
- Send one `--work-location-ids <uuid>` flag per selected work location. Omit it for global policies.
- Send both `--max-total-hours-window-weeks` and `--max-total-hours-per-window` together, or omit both.
- Send `--negative-balance-limit-minutes` only with `--calculation-mode FLEXIBLE_TIME_BALANCE`.
- On the confirmation turn, execution is the first functional step. Do not ask another question unless a required field is still missing or invalid.

### Required arguments
For a supported jurisdiction preset:
- `jurisdiction`

For a generic custom policy:
- `name`
- `enabled`
- `trigger_unit`
- `threshold_behavior`
- `threshold_source`

### Optional arguments
- `jurisdiction`
- `description`
- `calculation_mode`
- `negative_balance_limit_minutes`
- `threshold_hours`
- `weekdays_only`
- `weekends_only`
- `max_daily_overtime_hours`
- `max_daily_overtime_percent_of_normal_hours`
- `max_total_daily_hours`
- `max_monthly_overtime_hours`
- `max_yearly_overtime_hours`
- `max_extended_yearly_overtime_hours`
- `work_location_ids`
- `max_total_hours_window_weeks`
- `max_total_hours_per_window`
- `night_window_enabled`
- `night_window_start`
- `night_window_end`
- `night_premium_shift_worker_exclusion_enabled`
- `rest_day_compensation_mode`
- `max_consecutive_rest_day_work_days`
- `day_worker_rest_day_sequence_exemption_enabled`

### Execution
```text
Preferred execution: exec {"command":"python skills/attendance/generate_overtime_policy/scripts/generate_overtime_policy.py [--jurisdiction <UAE>] [--name \"<policy name>\"] [--enabled <true|false>] [--trigger-unit <DAILY|WEEKLY>] [--threshold-behavior <PROGRESSIVE|CLIFF>] [--threshold-source <SHIFT_TARGET|FIXED>] [--description \"<description>\"] [--calculation-mode <POSITIVE_OVERTIME_ONLY|TIME_BALANCE|FLEXIBLE_TIME_BALANCE>] [--negative-balance-limit-minutes <minutes>] [--threshold-hours <number>] [--weekdays-only <true|false>] [--weekends-only <true|false>] [--max-daily-overtime-hours <number>] [--max-daily-overtime-percent-of-normal-hours <number>] [--max-total-daily-hours <number>] [--max-monthly-overtime-hours <number>] [--max-yearly-overtime-hours <number>] [--max-extended-yearly-overtime-hours <number>] [--work-location-ids <uuid>] [--max-total-hours-window-weeks <weeks>] [--max-total-hours-per-window <hours>] [--night-window-enabled <true|false>] [--night-window-start <HH:mm:ss>] [--night-window-end <HH:mm:ss>] [--night-premium-shift-worker-exclusion-enabled <true|false>] [--rest-day-compensation-mode <NONE|PAY_PREMIUM|COMPENSATORY_DAY|HR_CHOICE>] [--max-consecutive-rest-day-work-days <days>] [--day-worker-rest-day-sequence-exemption-enabled <true|false>]"}
```
