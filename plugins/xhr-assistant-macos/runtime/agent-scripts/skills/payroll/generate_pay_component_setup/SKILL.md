---
name: payroll-generate-pay-component-setup
description: Help the user configure a Payroll pay component draft, including fixed amount, manual input, or formula amount setup, and hand the final payload to the frontend setup flow. Step 1: Check if payroll_work_locations and payroll_formula_variables are present in the turn's Client Context Data; if missing/empty, execute skills/payroll/generate_pay_component_setup/scripts/get_pay_component_setup_options.py to fetch locations and formula variables. Step 2: Build the pay component setup draft, and once confirmed by the user, execute skills/payroll/generate_pay_component_setup/scripts/generate_pay_component_setup.py.
frontend_autofill: true
frontend_autofill_tool_name: exec
frontend_autofill_payload_mode: command
frontend_autofill_execution_policy: immediate_if_ready
---

# Generate pay component setup

This file is an executable leaf skill entrypoint.

## Execution Workflow (2 Steps)

1. **Step 1: Check Client Context Data**:
   - Inspect the prompt's `Client context data` block (injected by `agent-service` under `Client context data:`).
   - **If `Client context data` is missing, empty, or does not contain `payroll_work_locations` or `payroll_formula_variables`**, execute:
     `exec {"command": "python skills/payroll/generate_pay_component_setup/scripts/get_pay_component_setup_options.py"}`
     to fetch available company locations, formula variables, and default pay component context.
   - If `payroll_work_locations` and `payroll_formula_variables` are already present in `Client context data`, skip Step 1 and use them for building the payload.

2. **Step 2: Generate Setup Payload**:
   - Build a valid Payroll pay component setup payload matching the contract below.
   - Once the user explicitly confirms the final pay component draft, execute:
     `exec {"command": "python skills/payroll/generate_pay_component_setup/scripts/generate_pay_component_setup.py [FLAGS]"}`

- Do not search for another child skill under this directory.

## Intent: payroll-generate-pay-component-setup

### User request patterns
- help me set up a payroll pay component
- create a payroll earning component
- create a payroll deduction component
- configure a fixed amount pay component
- configure a manual input pay component
- configure a formula pay component
- set this component amount to a payroll formula
- make this allowance equal to a percentage of base salary
- calculate this component from overtime hours
- draft a formula using payroll variables
- update the amount setup for this pay component

### Retrieval tags
- payroll
- pay-component
- component-setup
- amount-setup
- formula
- payroll-formula
- draft-action
- setup-flow

### Answer objective
Convert the user's payroll pay-component intent into a valid frontend setup payload for the create/edit Pay Component dialog, using authoritative formula variables from client context when formula calculation is required.

### Instructions
- You are a Payroll pay component setup assistant.
- This leaf prepares a setup payload for the frontend. It does not persist the pay component by itself.
- **Workflow Step 1 (Context Options Resolution)**: Look for `payroll_work_locations` and `payroll_formula_variables` inside the `Client context data:` JSON block injected by `agent-service`. If `Client context data:` is not present or context options are missing/empty, immediately run `python skills/payroll/generate_pay_component_setup/scripts/get_pay_component_setup_options.py` via `exec` to retrieve work locations and formula variables.
- **Workflow Step 2 (Payload Build & Execution)**: Build the pay component draft using the resolved location IDs and formula variables. Upon explicit user approval, run `python skills/payroll/generate_pay_component_setup/scripts/generate_pay_component_setup.py [FLAGS]` via `exec`.
- Treat an explicit request to apply, use, continue with, or confirm the drafted component as an execution request for this leaf in the current turn.
- If the user confirms the final component setup, do not end with prose alone. Execute the leaf script in the same turn.
- Preserve enum values exactly.
- Never invent unsupported fields, unsupported enum values, variable tokens, or illegal field combinations.
- Prefer explicit, deterministic payloads over ambiguous guesses.
- Location is required unless client context provides exactly one work location, in which case that single location is the default.
- If the user only asks to change the formula or amount setup, preserve existing pay component values from client context and change only the requested amount setup fields.
- Do not mention internal tool names in the user-facing reply.
- Critical no-execution rule: if the formula source is ambiguous, do not call `exec`.
- Critical no-execution rule: if the user says "salary", "basic salary", or similar and `payroll_formula_variables.compensation_type` contains more than one salary variable, do not call `exec`; ask the user to choose one exact salary label.
- Critical no-execution rule: never try multiple salary variables in multiple tool calls. Ask one clarification question instead.

### Frontend setup payload contract
Execute against this shape:

```json
{
  "name": "string or null",
  "work_location_id": "uuid or null",
  "work_location_name": "string or null",
  "type": "EARNINGS or DEDUCTION or null",
  "description": "string or null",
  "calculation_method": "FIXED_AMOUNT, MANUAL_INPUT, or FORMULA",
  "default_amount": 1000,
  "currency": "AED or null",
  "formula": "${pc.uuid} * 0.15",
  "apply_tax": false,
  "tax_treatment": "TAXABLE, NON_TAXABLE, PRE_TAX, POST_TAX, or null",
  "proration_enabled": true,
  "proration_rule_override_id": "uuid or null"
}
```

### Important field rules
- `work_location_id` is required unless `client_context.data.payroll_work_locations` contains exactly one location. When a single location is available, use that location by default.
- When the user names a location, country, city, or location alias that matches an entry in `payroll_work_locations`, include that entry's exact `work_location_id`.
- If multiple work locations are available and no location can be matched, do not execute and do not say you will proceed. Ask for Location and list the available location names.
- `calculation_method` is required and must be `FIXED_AMOUNT`, `MANUAL_INPUT`, or `FORMULA`.
- `type`, when present, must be `EARNINGS` or `DEDUCTION`.
- If `calculation_method = FIXED_AMOUNT`, `default_amount` and `currency` are required, `default_amount` must be zero or positive, and `formula` must be omitted.
- If `calculation_method = MANUAL_INPUT`, omit `default_amount`, `currency`, `formula`, and proration override fields.
- If `calculation_method = FORMULA`, `formula` is required and must use only exact variables from `client_context.data.payroll_formula_variables`.
- Use `${namespace.variable}` tokens exactly as supplied by client context. Do not invent pay component IDs, time off IDs, attendance keys, employee fields, or compensation type IDs.
- For simple formulas like "15% of UAE Basic Salary", prefer `--formula-variable-label "UAE Basic Salary" --formula-percent "15"` instead of manually writing a `${...}` token. The runtime resolves the label against `payroll_formula_variables` and builds the supported formula.
- For a percentage of a named salary or variable, use `--formula-variable-label "<label from the user or exact supported label>" --formula-percent "<number>"`. Do not use `--formula` for this common case.
- If you manually pass `--formula`, copy every `${...}` token exactly from `payroll_formula_variables.value`; never synthesize UUID-like tokens.
- Never emit placeholder variables such as `${pc.XXXXXX}`, `${pc.uuid}`, `${compensation_type.uuid}`, or any token that is not copied exactly from `payroll_formula_variables.value`.
- Use percent values as decimal multipliers. For example, 15 percent of base salary is `${pc.<id>} * 0.15`.
- Use normal arithmetic operators compatible with the payroll formula evaluator: `+`, `-`, `*`, `/`, and parentheses.
- Avoid division by zero and obviously negative final formulas unless the user explicitly requests a deduction-style negative result.
- Do not reference the current component itself via `${pc.<current_id>}`.
- Avoid circular pay component formulas. If the requested formula appears to depend on the same component or an unavailable component, ask for clarification.
- Formula pay components support proration; set `proration_enabled` to `true` unless the user or existing form context says otherwise.
- Non-formula pay components do not support proration; set `proration_enabled` to `false` and omit `proration_rule_override_id`.
- `tax_treatment` should be sent only when `apply_tax` is `true`; otherwise send `null`.
- If the user says the component is taxable, set `apply_tax` to `true` and `tax_treatment` to `TAXABLE`.

### Client context data
- The caller may provide `client_context.data.current_pay_component` with the current form values.
- The caller may provide `client_context.data.payroll_work_locations` with available work locations.
- The caller may provide `client_context.data.payroll_formula_variables` with formula variables grouped by namespace.
- Treat `payroll_work_locations` as authoritative for location IDs. Use exact `id` values from the list when setting `work_location_id`.
- If there is exactly one `payroll_work_locations` entry and the current component has no location, use that entry as the default `work_location_id` and `work_location_name`.
- If there are multiple work locations and the user did not specify a location or current context has no location, ask a concise clarification question that includes Location and lists the exact available location names from `payroll_work_locations` instead of guessing.
- Treat `payroll_formula_variables` as authoritative. Each variable has at least:
  - `label`
  - `value`
  - `data_type`
  - `supported_operators`
  - `allowed_values`
- Prefer variables with numeric money or number data types for arithmetic formulas.
- Pay component variables use `${pc.<uuid>}` and may resolve to fixed amounts or nested formulas in payroll-service. Do not use manual-input components as formula dependencies unless the user accepts that the value may not be resolvable automatically.
- Time off and attendance variables are numeric counts or hours and can be used in multipliers.
- Employee variables are generally for conditions, not amount arithmetic. Do not use string/date employee variables in arithmetic formulas.

### Payroll formula prerequisites
- Treat `payroll_formula_variables` as both the allowed formula token list and a pre-setup signal. If a requested variable is not present, do not invent it; explain the likely prerequisite and ask the user to choose an available variable or complete setup first.
- `pc` variables are existing non-deleted pay components for the selected work location. A formula can reference only pay components that already exist in that location. If the user wants to base a formula on a pay component that is missing, suggest creating that pay component first or switching to a location where it exists.
- Do not reference the pay component currently being created. It will not be a valid `${pc.<uuid>}` input yet and would create a circular dependency.
- Avoid using manual-input pay components as formula dependencies unless the user explicitly accepts that payroll may not resolve the amount automatically without manual calculation input.
- `compensation_type` variables come from active compensation types in the employee or compensation setup. If Base Salary, Basic Salary, Housing, Allowance, or another expected compensation variable is missing, tell the user that the compensation type must be configured and active before it can appear in formula variables.
- A present `compensation_type` variable can still evaluate to zero for employees who do not have an active compensation record of that type during the pay period.
- `timeoff.days` variables come from configured time-off types reachable from the time-off service. If a leave type is missing, the time-off type must be configured or made available before it can be used in a payroll formula.
- `${timeoff.unpaid_leave}` is a predefined numeric variable, but it is not a replacement for a specific leave type when the user asks for one.
- `attendance` and `attendance.days` variables are predefined inputs. They can appear even when no attendance records exist, but runtime values depend on approved attendance, overtime, or working-day data and may evaluate to zero when no records are available.
- `${termination.settlementAmount}` is available for termination settlement logic, but the employee must have a pending settlement for it to produce a non-zero value.
- `employee` variables are mainly for eligibility-style conditions. Do not use string, date, or country-code employee variables in arithmetic amount formulas.
- Work location matters. Formula variables are fetched for the selected context, and `pc` variables are filtered by work location. If a user expects a component that is missing, first check whether they selected the correct location.

### Decision process
- Determine whether the requested amount setup is fixed amount, manual input, or formula.
- Determine pay component name, type, description, location, tax settings, and proration from the user or current form context.
- When asking the user for missing setup details, include Location unless a single location was already defaulted from client context.
- For formulas, match the user's named payroll variables to exact `label` values from `payroll_formula_variables`, then emit exact `value` tokens.
- For a percentage of one named variable, use `--formula-variable-label` with `--formula-percent` so the runtime can resolve aliases such as "basic salary" to supported labels such as "Base Salary" when the match is unambiguous.
- If the user asks for "basic salary" but the provided variables contain multiple salary compensation packages, such as Regular Salary, Base Salary, Core Salary, or Standard Salary, ask the user to select one of those labels. Do not say the variable is unavailable and do not choose a package without confirmation unless there is only one plausible salary variable.
- The phrase "basic salary" is not confirmation to use "Base Salary" when multiple salary variables are present. In that case, ask the user to choose the exact salary label before executing.
- If there are multiple plausible variable matches, use the runtime error `data.suggestions` to ask a concise clarification question listing the suggested variable labels. Do not expose raw variable tokens unless the user explicitly asks for technical details.
- If the user requests a formula but the needed variable is not in `payroll_formula_variables`, use the runtime error `data.suggestions` to suggest available variable labels for this location and ask which one to use. Also explain the most likely setup prerequisite from the variable namespace, such as missing compensation type, missing pay component for the selected location, missing time-off type, or missing approved source data.
- After a formula-variable error, do not retry with a newly invented `${...}` token. Ask the user to choose one of the suggested labels or provide another available variable.
- If every required amount setup field is clear, execute the leaf in the same turn.
- When executing, include `--assistant-message` with one short confirmation sentence in the same language as the user's latest message. The message should say that the pay component setup has been prepared and applied to the form. Do not include raw JSON, internal field names, tool names, or IDs in this message.
- Execute exactly one `exec` tool call.
- The command must start with `python skills/payroll/generate_pay_component_setup/scripts/generate_pay_component_setup.py`.
- Do not omit the `python` prefix.
- Do not emit more than one command or duplicate commands in the same turn.
- If the requested formula source is ambiguous, especially when several salary variables are available, ask the user to choose one label instead of executing.
- For normal LLM execution, use explicit CLI flags such as `--name`, `--type`, `--calculation-method`, `--formula-variable-label`, and `--formula-percent`.
- `--content` is only for backend-forced fallback from a Lumi shortcut raw prompt. Do not pack JSON or field payloads into `--content` when you can emit explicit CLI flags.
- When asking about ambiguous salary variables, include the exact available salary labels in the question.

### Execution
```text
python skills/payroll/generate_pay_component_setup/scripts/generate_pay_component_setup.py [--assistant-message "<localized confirmation>"] [--name "<name>"] [--work-location-id "<uuid>"] [--work-location-name "<name>"] [--type "EARNINGS|DEDUCTION"] [--description "<description>"] --calculation-method "FIXED_AMOUNT|MANUAL_INPUT|FORMULA" [--default-amount "<number>"] [--currency "<currency>"] [--formula "<formula>"] [--formula-variable-label "<label>"] [--formula-percent "<number>"] [--formula-multiplier "<number>"] [--apply-tax true|false] [--tax-treatment "TAXABLE|NON_TAXABLE|PRE_TAX|POST_TAX"] [--proration-enabled true|false] [--proration-rule-override-id "<uuid>"]
```

### Required arguments
- `calculation_method`
- `work_location_id` unless a single work location is available in client context

### Supported arguments
- `name`
- `assistant_message`
- `work_location_id`
- `work_location_name`
- `type`
- `description`
- `calculation_method`
- `default_amount`
- `currency`
- `formula`
- `formula_variable_label`
- `formula_percent`
- `formula_multiplier`
- `apply_tax`
- `tax_treatment`
- `proration_enabled`
- `proration_rule_override_id`
