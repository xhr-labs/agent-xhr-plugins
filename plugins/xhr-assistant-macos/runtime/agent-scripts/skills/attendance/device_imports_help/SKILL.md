---
name: attendance-device-imports-help
description: Explain Attendance device CSV imports. Use when the user asks how to upload attendance-device data, map CSV columns or employees, review imported rows, or check an import job.
---

# Device Imports Help

## Intent: attendance-device-imports-help
### User request patterns
- import attendance device data
- upload an attendance CSV
- map device import columns
- import clock records for employees
- review attendance import rows
- check an attendance import job
- do I need Device Imports
- why did my attendance import fail
- why are imported rows not valid
- why is my import still processing

### Retrieval tags
- attendance
- device-imports
- csv
- timesheets
- employee-mapping
- optional-workflow
- direct-answer
- troubleshooting
- async-job

### Answer objective
Explain the optional CSV import workflow, its shift resolution options, and the required review before submission.

### Instructions
- Answer directly without calling an executable tool; no device-import runtime leaf is available.
- Explain that Device Imports is optional and is intended for attendance-device CSV exports.
- Mention the permission boundary: the menu is available to users with report or configuration edit access, while backend authorization still applies.
- Do not tell users to configure a roster just to import device data.

### Direct answer
Open [Device Imports]({{attendance_device_imports_url}}).

Device Imports is an optional workflow for bringing attendance records from a device CSV export into Attendance Tracking. It is useful when employees clock in through an external attendance device instead of entering times manually or using the in-app clock.

The usual flow is:

1. Upload the device CSV.
2. Map the CSV columns and map the device employees to X-HR employees.
3. Optionally select one active shift for the whole import. If you leave it unset, each row can resolve its shift from the mapped `shift_code` column.
4. Review the backend-inferred rows and fix any mapping or validation issues.
5. Submit the reviewed import and monitor the asynchronous job status.

Device Imports does not require Manual or Advanced roster setup. Employees still need the correct shift or schedule context for the imported rows to be valid. If rows fail validation, review employee mapping, shift resolution, dates and times, duplicates or overlaps, and the backend-inferred row details before submitting again. If the job is still processing, use its asynchronous status rather than starting a duplicate import.
