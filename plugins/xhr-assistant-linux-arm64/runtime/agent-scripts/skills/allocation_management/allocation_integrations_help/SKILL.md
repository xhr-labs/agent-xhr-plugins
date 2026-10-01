---
name: allocation-management-integrations-help
description: Explain Allocation Management integrations. Use when the user asks about YouTrack, Workbench, X-HR, Attendance Tracking, sync, connection tests, or switching the active integration.
---

# Allocation Integrations Help

## Intent: allocation-management-integrations-help
### User request patterns
- connect Allocation Management to YouTrack
- sync Workbench projects into Allocation Management
- connect Attendance Tracking to allocation reports
- test an allocation integration
- switch the active allocation platform
- troubleshoot unmapped timesheet rows
- retry a failed synchronization

### Retrieval tags
- allocation-management
- integrations
- youtrack
- workbench
- attendance-tracking
- sync
- unmapped-data
- direct-answer

### Answer objective
Explain supported integration use cases, prerequisites, sync lifecycle, data-quality symptoms, and guarded switching behavior.

### Instructions
- Answer directly without calling executable tools.
- State that integrations are optional for core monthly allocation planning.
- Explain the two visible platform choices accurately: X-HR Platform can bring in Workbench projects and approved Attendance task timesheets; YouTrack can bring in projects and work items through its configured connection.
- Tell an Admin to enter the connection details, test the connection, save the configuration, preview external projects, select the projects to import, and choose a date range before starting a full sync.
- Explain that only one platform is active at a time. Switching is intentional and can change the source used for imported project and timesheet data.
- Explain sync statuses in user terms: running/queued means wait, success means completed, partial means some rows need attention, failed means review the error and retry after fixing the connection or data.
- Explain that a failed or partial sync can be retried; an already-running sync should not be started again.
- Explain unmapped projects or employees as incomplete reporting mappings. Imported raw work may remain visible in Timesheet while excluded from aggregate variance until both project and employee mapping are available.
- Warn users to regenerate or rotate exposed connection/webhook credentials and not paste secrets into chat. Do not display raw tokens in answers.

### Direct answer
Open [Allocation Management Integrations]({{allocation_integrations_url}}).

Allocation Management integrations connect resource planning with operational systems. Supported flows include YouTrack configuration, Workbench project sync, X-HR Platform integration, and approved Attendance Tracking task data for reporting.

Integration setup includes connection testing, previewing projects, selecting what to import, choosing a date range, and reviewing the sync result. If another integration is already active, switching should be treated as an intentional Admin action because it changes the source used for imported projects and actual-work reporting.

Use the Timesheet menu to inspect imported rows. A row marked unmapped is useful for diagnosing missing employee or project mapping; it is not proof that the sync failed.
