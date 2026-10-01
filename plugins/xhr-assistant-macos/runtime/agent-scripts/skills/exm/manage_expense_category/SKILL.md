---
name: exm-manage-expense-category
description: Create, rename, or delete an expense category in the Expense Management configuration after explicit confirmation.
side_effect: write
idempotency: key
---

# Manage Expense Category

## Intent: exm-manage-expense-category
### User request patterns
- add an expense category
- create a Travel expense category
- rename the Meals expense category
- update the description of an expense category
- delete an unused expense category
- change the code of an expense category
- yes, create that expense category

### Retrieval tags
- exm
- expense-management
- expense-categories
- category-configuration
- create-category
- delete-category
- write-action

### Answer objective
Apply exactly one confirmed category change - create, update, or delete - and report the resulting configuration.

### Instructions
- **Never execute this script in a turn where the user asked not to act yet.** Wording such as "show me first", "do not change it yet", "just check", "preview it", "chua doi", or "khoan doi" means: write the preview, ask for confirmation, and call NO tool that writes. Executing in that turn is wrong even when every argument is already known and even when the preview is shown alongside it.
- This is company-wide configuration and needs configuration write access. `permission_denied` means the caller is not an Expense Management admin: say so, point them to their admin, and do not retry.
- Before `update` or `delete`, resolve the exact category with `skills/exm/list_expense_categories` and keep its name visible. Never guess a category UUID.
- Field rules: `--name` is required to create and must be unique enough to be recognizable. `--code` may contain only letters, numbers, hyphens, and underscores. `--description` is limited to 500 characters.
- Before `delete`, run `skills/exm/list_expense_categories --view deletion_eligibility --category-id <uuid>`. When `canDelete` is false, tell the user how many expense items reference the category and that it cannot be deleted; do not attempt the delete.
- Deleting a category only stops it being offered for new expenses; existing expenses keep their category snapshot. Say this in the preview so the user is not misled.
- **Mandatory user confirmation and turn boundary**:
  - Before executing, ALWAYS present a preview:
    - **Action**: `Create`, `Update`, or `Delete`
    - **Category**: `<current name>` (for update and delete)
    - **New name / code / description**: `<values or "unchanged">`
  - Ask: *"Do you confirm this change to the expense categories?"*
  - STOP and wait for explicit confirmation in a later turn. DO NOT execute the script in the same turn as the preview.
- After a successful run, restate the final category name, code, and description. Never print the category ID or any other UUID.
- On a backend validation error, report the message and ask the user; do not retry with altered values.

### Required arguments
- `action`: `create`, `update`, or `delete`.
- `category_id`: Category UUID; required for `update` and `delete`.
- `name`: Category name; required for `create`.

### Optional arguments
- `code`: Short category code; letters, numbers, hyphens, and underscores only.
- `description`: Category description, 500 characters or fewer.
- `idempotency_key`: Optional idempotency key; the script generates one when omitted.

### Execution
```text
python skills/exm/manage_expense_category/scripts/manage_expense_category.py --action create --name "<name>" [--code <code>] [--description "<text>"]
python skills/exm/manage_expense_category/scripts/manage_expense_category.py --action update --category-id <uuid> [--name "<name>"] [--code <code>] [--description "<text>"]
python skills/exm/manage_expense_category/scripts/manage_expense_category.py --action delete --category-id <uuid>
```
