---
name: exm-list-expense-categories
description: List the company's expense categories and resolve a category name to its ID, or read one category's activity log or deletion eligibility.
side_effect: read
---

# List Expense Categories

## Intent: exm-list-expense-categories
### User request patterns
- show the expense categories
- what expense categories can I use
- list the expense category configuration
- which category should I use for a taxi ride
- how many expenses use the Travel category
- show who changed the Meals category
- check whether this expense category can be deleted
- show the activity log for an expense category

### Retrieval tags
- exm
- expense-management
- expense-categories
- category-configuration
- category-activity-log
- category-lookup

### Answer objective
Return the company's expense categories with their names, codes, descriptions, and usage counts, or the requested single-category detail, and keep the category ID available for follow-up calls.

### Instructions
- Run this leaf whenever another expense tool needs a `category_id`. Never guess a category UUID and never reuse one from an earlier conversation without re-reading.
- Views:
  - `--view list` (default): every configured category.
  - `--view activity_logs --category-id <uuid>`: who created or edited that category and when.
  - `--view deletion_eligibility --category-id <uuid>`: whether the category can be deleted and how many expense items reference it.
- Present the list as a Markdown table: category name, code, description, number of expense items using it (`referenceCount`). Say "not set" for an empty code or description.
- When the user asks which category fits a purchase, name the best matching category from the returned list and say it is a suggestion; never invent a category that is not in the list.
- Never print category IDs, actor employee IDs, or any UUID in the reply.
- When no category exists yet, say so plainly and mention that an administrator adds categories in [Expense Management categories]({{expenses_categories_url}}). That is not an error.
- A category with `referenceCount` above zero cannot be deleted; direct that question to `manage_expense_category` only after checking `--view deletion_eligibility`.
- Reading categories needs configuration read access. `permission_denied` means the caller cannot see the configuration - say so and point them to an Expense Management admin.

### Optional arguments
- `view`: `list` (default), `activity_logs`, or `deletion_eligibility`.
- `category_id`: Category UUID; required for `activity_logs` and `deletion_eligibility`.

### Execution
```text
python skills/exm/list_expense_categories/scripts/list_expense_categories.py [--view list|activity_logs|deletion_eligibility] [--category-id <uuid>]
```
