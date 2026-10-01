---
name: exm-expense-permissions-help
description: Explain Expense Management access - app access versus datablock permissions for categories, policies, and app permissions, what each role can see, and where approval rights actually come from.
---

# Expense Management Permissions

## Intent: exm-expense-permissions-help
### User request patterns
- who can access the Expense Management app
- how do I give someone access to expense categories
- why can I not see the Categories menu
- what permissions does the expenses app have
- how do I make someone an expense admin
- can I control who approves expenses from app permissions
- why is the Policies menu missing for me

### Retrieval tags
- exm
- expense-management
- app-permissions
- datablocks
- access-control
- direct-answer

### Answer objective
Explain the two permission layers of the app, what each datablock unlocks, and which access question is answered somewhere else.

### Instructions
- Answer directly without calling executable tools.
- Do not claim a permission state or change it; permission changes are made in the app by an authorized admin.
- Keep approval rights and app permissions clearly separate - confusing them is the most common mistake here.

### Direct answer
Expense Management has two permission layers, both managed in [App Permissions]({{expenses_app_permissions_url}}).

**App Access** decides who can open and use the app at all - all employees, or specific roles, departments, teams, or people.

**Permissions** then grant view or edit on individual datablocks. `categories` controls the Categories configuration screen, `policies` controls the Policies screen, and `app_permissions` controls the permission screen itself. View lets a user read the screen; edit lets them change it, and edit implies view. A menu entry disappears entirely when you have no view access to its datablock, which is why Categories or Policies can be missing for you while a colleague sees them.

My Expenses is available to anyone who can access the app, since everyone claims their own expenses. Approvals appears only when you actually have approval tasks.

Who may **approve** an expense is not set here. Approval routing is owned by the platform's Workflows engine through the expense approval workflow; the default sends approvals to Admin and HR Manager roles. Change approvers there, not in App Permissions.
