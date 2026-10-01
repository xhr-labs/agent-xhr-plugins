---
name: exm-manage-expense-policy
description: Create, edit, enable, disable, archive, or delete an expense policy, and run the two read-only checks the app runs before saving - overlap conflict check and policy evaluation preview.
side_effect: write
idempotency: key
read_actions: check_conflict, evaluate_preview
---

# Manage Expense Policy

## Intent: exm-manage-expense-policy
### User request patterns
- create an expense policy
- set a 100 USD per-day meal limit
- require a receipt for every expense above 50 USD
- disable the travel expense policy
- enable an expense policy again
- archive an old expense policy
- delete an unused expense policy
- check whether this policy conflicts with an existing one
- preview what this policy would do to an expense
- yes, save that expense policy

### Retrieval tags
- exm
- expense-management
- expense-policies
- spending-limits
- policy-rules
- policy-lifecycle
- write-action

### Answer objective
Apply exactly one confirmed expense-policy operation, or run one read-only policy check, and report the resulting policy state or check outcome.

### Instructions
- **Never execute this script in a turn where the user asked not to act yet.** Wording such as "show me first", "do not save it yet", "just check", "preview it", "chua luu", or "khoan luu" means: write the preview, ask for confirmation, and call NO tool that writes. Executing in that turn is wrong even when every argument is already known and even when the preview is shown alongside it.
- Expense policies are configuration guarded by the `policies` datablock and are not enabled in every environment. `permission_denied` or `not_found` means the caller cannot manage policies here: say so and stop.
- Always read the current state first with `skills/exm/list_expense_policies` (and `--policy-id` for an edit). Never guess a policy UUID and never edit from memory.
- Actions: `create`, `update`, `enable`, `disable`, `archive`, `delete`, `check_conflict`, `evaluate_preview`.
- `create` requires `--name`, `--effective-from`, and `--rules-json` with at least one rule. `--priority` defaults to 100 and `--enabled` defaults to true.
- `--rules-json` is a JSON array. Each rule needs `ruleType` and, depending on it, more fields:
  - `ruleType` one of `CATEGORY_ACCESS`, `AMOUNT_LIMIT`, `RECEIPT_REQUIRED`, `DESCRIPTION_REQUIRED`, `SUBMISSION_WINDOW`, `FUTURE_DATE_BLOCKED`, `CLIENT_REQUIRED`, `PROJECT_REQUIRED`, `ATTENDEES_REQUIRED`, `MERCHANT_REQUIRED`, `MERCHANT_RESTRICTION`, `PAYMENT_METHOD_RESTRICTION`, `FLIGHT_CABIN_RESTRICTION`, `MILEAGE_RATE`, `PER_NIGHT_LIMIT`, `PER_ATTENDEE_LIMIT`.
  - `severity` one of `HARD_BLOCK`, `SOFT_WARNING`, `INFO` (default `SOFT_WARNING`). `HARD_BLOCK` stops submission, the others only warn - confirm which one the user means before saving.
  - `period` one of `PER_EXPENSE`, `PER_DAY`, `PER_WEEK`, `PER_MONTH`, `PER_QUARTER`, `PER_YEAR`, `PER_TRIP`, `PER_NIGHT`, `PER_ATTENDEE`, `PER_DISTANCE_UNIT` (default `PER_EXPENSE`).
  - `AMOUNT_LIMIT` needs `limitAmount` (and normally `limitCurrency`). `CATEGORY_ACCESS` needs `access` (`ALLOWED`, `NOT_ALLOWED`, `ALLOWED_WITH_WARNING`). A `thresholdAmount` needs a `thresholdCurrency`.
  - `categoryId` restricts the rule to one category; omit it to apply to all categories. Resolve it with `skills/exm/list_expense_categories`.
- `--eligibility-json` takes `{"all": [...], "any": [...], "none": [...]}` condition lists. Omit it, or send empty lists, to apply the policy to every employee in the company.
- Before `create` or a rule-changing `update`, run `--action check_conflict` with the same fields and report any overlapping policy to the user. Both `check_conflict` and `evaluate_preview` are read-only dry runs and change nothing.
- `--action evaluate_preview --preview-json '<draft expense>'` runs the policy engine against a draft expense without saving anything. Use it to answer "what would happen if" questions.
- **Check the backend's own permission flags before choosing an action.** Every policy read returns `can_edit_rules`, `can_delete`, `can_archive`, and `usage_count`. When `can_delete` is false, do NOT call `--action delete` at all - answer that the policy has evaluation history and offer `--action archive`. When `can_edit_rules` is false, do NOT send `--rules-json` - only metadata, the enabled switch, and safe dates can change; offer a replacement policy for rule changes. Letting the backend reject the call (`409 POLICY_DELETE_BLOCKED`) instead of reading the flag is wrong: the flag is there so the user gets an explanation rather than an error.
- **Mandatory user confirmation and turn boundary** (applies to `create`, `update`, `enable`, `disable`, `archive`, `delete`; not to the two read-only checks):
  - Before executing, ALWAYS present a preview:
    - **Action**: `<action>`
    - **Policy**: `<name>`
    - **Lifecycle**: enabled `<on/off>`, priority `<n>`, effective `<from>` to `<to or "open ended">`
    - **Eligibility**: `<summary or "all employees">`
    - **Rules**: one line per rule with type, severity, period, and limit
  - Ask: *"Do you confirm this expense policy change?"*
  - STOP and wait for explicit confirmation in a later turn. DO NOT execute the script in the same turn as the preview.
- After a successful run, restate the policy name, status, enabled state, and effective dates. Never print policy IDs, rule IDs, or any UUID.
- On a backend validation or conflict error, report the message and ask the user; do not retry with altered values.

### Required arguments
- `action`: `create`, `update`, `enable`, `disable`, `archive`, `delete`, `check_conflict`, or `evaluate_preview`.
- `policy_id`: Policy UUID; required for `update`, `enable`, `disable`, `archive`, and `delete`, optional for `check_conflict`.
- `name`: Policy name; required for `create` and `check_conflict`.
- `effective_from`: Start date (`YYYY-MM-DD`); required for `create` and `check_conflict`.
- `rules_json`: JSON array of rules; required for `create` and `check_conflict`.

### Optional arguments
- `description`: Policy description.
- `enabled`: `true` or `false`; the evaluation switch.
- `priority`: Integer priority; lower numbers are evaluated first.
- `effective_to`: End date (`YYYY-MM-DD`); omit for an open-ended policy.
- `eligibility_json`: `{"all": [...], "any": [...], "none": [...]}` eligibility conditions.
- `preview_json`: Draft expense payload for `evaluate_preview`.
- `idempotency_key`: Optional idempotency key; the script generates one when omitted.

### Execution
```text
python skills/exm/manage_expense_policy/scripts/manage_expense_policy.py --action create --name "<name>" --effective-from YYYY-MM-DD --rules-json '<json array>' [--description "<text>"] [--priority N] [--enabled true] [--effective-to YYYY-MM-DD] [--eligibility-json '<json>']
python skills/exm/manage_expense_policy/scripts/manage_expense_policy.py --action update --policy-id <uuid> [--name "<name>"] [--rules-json '<json array>']
python skills/exm/manage_expense_policy/scripts/manage_expense_policy.py --action enable|disable|archive|delete --policy-id <uuid>
python skills/exm/manage_expense_policy/scripts/manage_expense_policy.py --action check_conflict --name "<name>" --effective-from YYYY-MM-DD --rules-json '<json array>' [--policy-id <uuid>]
python skills/exm/manage_expense_policy/scripts/manage_expense_policy.py --action evaluate_preview --preview-json '<json object>'
```
