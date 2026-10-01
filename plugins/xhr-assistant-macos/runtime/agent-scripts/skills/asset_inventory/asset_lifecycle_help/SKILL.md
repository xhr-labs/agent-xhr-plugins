---
name: asset-inventory-asset-lifecycle-help
description: Explain Asset Inventory lifecycle actions. Use when the user asks about assigning, returning, pending return, acknowledgement, asset edit, asset detail, status changes, or activity timeline.
---

# Asset Lifecycle Help

## Intent: asset-inventory-asset-lifecycle-help
### User request patterns
- assign an asset to an employee
- return an assigned asset
- mark an asset pending return
- view asset activity history
- edit asset status or details

### Retrieval tags
- asset-inventory
- lifecycle
- assign
- return
- activity-timeline
- direct-answer

### Answer objective
Explain the admin lifecycle flow and status-aware actions for assets.

### Instructions
- Answer directly without calling executable tools.
- Mention that visible actions depend on status and permission.

### Direct answer
Open the [Asset Register]({{asset_register_url}}) to manage asset lifecycle actions.

Asset managers can manage lifecycle actions from the asset list or asset detail page. Available actions depend on the asset status and the user's permission.

Typical lifecycle flow:

1. **In stock** assets can be assigned to an employee.
2. **Assigned** assets can be flagged for return or returned when the employee gives them back.
3. **Pending return** assets can be completed as returned.
4. Employees may acknowledge receipt when that step is part of the assignment flow.

The asset detail page includes inventory metadata and an activity timeline so admins can review assignment, return, acknowledgement, update, and status-change events.
