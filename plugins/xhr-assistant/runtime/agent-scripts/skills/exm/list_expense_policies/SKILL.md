---
name: exm-list-expense-policies
description: List the company's expense policies with status, enabled state, priority, effective dates, and usage, or read one policy in full with its eligibility conditions and rules.
side_effect: read
---

# List Expense Policies

## Intent: exm-list-expense-policies
### User request patterns
- show the expense policies
- what is the expense limit for meals
- list the active expense policies
- show which expense policies are disabled
- read the rules of an expense policy
- which policy blocks expenses without a receipt
- show the effective dates of the travel expense policy
- check whether an expense policy is still in use

### Retrieval tags
- exm
- expense-management
- expense-policies
- spending-limits
- policy-rules
- policy-configuration

### Answer objective
Return the expense policies that match the filter, or one policy with its lifecycle, eligibility conditions, and ordered rules, so the user can see which spending limits apply.

### Instructions
- Expense policies are a configuration feature guarded by the `policies` datablock and are not enabled in every environment. If the tool returns `not_found` or `permission_denied`, tell the user that expense policies are not available to them in this environment and stop; do not retry with other arguments.
- Without `--policy-id` the tool lists policies. Filters: `--status` (`DRAFT`, `SCHEDULED`, `ACTIVE`, `ARCHIVED`), `--enabled true|false`, `--keyword`, `--page`, `--size`.
- With `--policy-id <uuid>` the tool returns one policy including `eligibility_expression` and `rules`. Resolve the UUID from the list first; never guess it.
- Present the list as a Markdown table: policy name, status, enabled, priority, effective dates, rule count, usage count. Render `status` and the enabled flag in plain language ("Active", "Draft", "Scheduled", "Archived"; "on" / "off").
- Status and the enabled switch are different things: a policy can be `ACTIVE` but switched off, in which case it is not evaluated. Say both explicitly and never treat one as the other.
- For a single policy, list each rule as: rule type in plain language, severity (hard block, soft warning, info), period, category (or "all categories"), limit or threshold with its currency, and the message. Keep the rule order returned by the backend - lower `sort_order` is evaluated first.
- An empty `eligibility_expression` means the policy applies to every employee in the company; say that instead of showing an empty condition list.
- Never print policy IDs, rule IDs, category IDs, or any UUID in the reply.
- `usage_count` above zero means submitted expenses already reference this policy. Report the accompanying `can_edit_rules`, `can_delete`, and `can_archive` flags as the authority on what is still possible, and keep them for any follow-up action - they are what `manage_expense_policy` must be driven by.
- To change a policy use `skills/exm/manage_expense_policy`. For a conceptual question about rule types and severities, read `skills/exm/expense_policies_help`.

### Optional arguments
- `policy_id`: Policy UUID; returns one policy with eligibility and rules instead of the list.
- `status`: `DRAFT`, `SCHEDULED`, `ACTIVE`, or `ARCHIVED`.
- `enabled`: `true` or `false`; filters on the evaluation switch.
- `keyword`: Free-text search over the policy name.
- `page`: Zero-based page number.
- `size`: Page size, 1-100, default 20.

### Execution
```text
python skills/exm/list_expense_policies/scripts/list_expense_policies.py [--status ACTIVE] [--enabled true] [--keyword text] [--page N] [--size N]
python skills/exm/list_expense_policies/scripts/list_expense_policies.py --policy-id <uuid>
```
