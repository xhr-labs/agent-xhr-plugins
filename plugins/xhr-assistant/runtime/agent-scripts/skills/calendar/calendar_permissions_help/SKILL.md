---
name: calendar-permissions-help
description: Explain Calendar app permissions and ReBAC checks. Use when the user asks who can access calendar pages, appointment schedules, integrations, or why a calendar action is hidden.
---

# Calendar Permissions Help

## Intent: calendar-permissions-help
### User request patterns
- why can't I access Calendar
- manage calendar permissions
- who can edit appointment schedules
- why is a calendar action hidden
- explain calendar ReBAC permissions

### Retrieval tags
- calendar
- permissions
- rebac
- appointment-schedule
- direct-answer

### Answer objective
Explain permission-aware access for calendar features.

### Instructions
- Answer directly without calling executable tools.

### Direct answer
Calendar pages and actions can be permission-aware. Access may depend on app installation, app access settings, data-block permissions, and relationship-based checks for the specific calendar, schedule, or integration.

If a user cannot see a page or action, confirm that Calendar is enabled for the tenant, the user has app access, and the relevant read or write permission is assigned.
