---
name: employee-helpdesk-get-hr-report-overview
description: Read the privacy-safe monthly Employee Helpdesk HR overview report for an authorized HR manager.
side_effect: read
---

## Intent: employee-helpdesk-get-hr-report-overview
### User request patterns
- show HR request overview for September
- review HR SLA and ageing report
- show HR workload and assignment report
- report on Employee Helpdesk requests

### Retrieval tags
- employee-helpdesk
- reports
- sla
- ageing
- workload
- read-action

### Answer objective
Retrieve the selected month and filters from the HR report projection.

### Instructions
- Use `month` in `YYYY-MM` format when supplied.
- Report access is independent from request-detail access; surface backend availability errors without fabricating data.

### Execution
`python skills/employee_helpdesk/get_hr_report_overview/scripts/get_hr_report_overview.py [--month YYYY-MM] [filters]`
