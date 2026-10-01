---
name: exm-expense-categories-help
description: Explain expense categories - what they are for, the name, code, and description fields, the activity log, and why a category that is already used cannot be deleted - without calling tools.
---

# Expense Categories (How-to)

## Intent: exm-expense-categories-help
### User request patterns
- what are expense categories for
- how do I add an expense category
- what is the code field on an expense category
- why can I not delete an expense category
- who can change expense categories
- how do I see who edited an expense category
- what happens to old expenses if I delete a category

### Retrieval tags
- exm
- expense-management
- expense-categories
- category-configuration
- activity-log
- direct-answer

### Answer objective
Explain what categories control, how they are configured, and the deletion and audit rules around them.

### Instructions
- Answer directly without calling executable tools.
- Do not claim a category exists or was changed; use `skills/exm/list_expense_categories` and `skills/exm/manage_expense_category` for live data and changes.

### Direct answer
Categories group spending - Travel, Meals, Accommodation - and every expense must have exactly one. They live under Configuration in [Categories]({{expenses_categories_url}}) and are visible only to users with configuration read access; editing needs write access.

A category has a **Category name** (required), an optional **Code** limited to letters, numbers, hyphens, and underscores, and an optional **Description** of up to 500 characters. The list shows how many expense items currently use each category.

Deletion is restricted. A category that is referenced by expense items cannot be deleted, and the app shows the reference count and disables the action; the app checks eligibility before offering **Delete**. When deletion is allowed, it only stops the category being offered on new expenses - expenses that already used it keep their recorded category, so history stays intact.

Every create and edit is recorded. **View activity** on a category shows who created or edited it, when, and which fields changed.
