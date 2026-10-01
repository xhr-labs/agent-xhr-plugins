---
name: employee-helpdesk-submit-help
description: Answer direct questions about submitting an Employee Helpdesk request, required answers, attachments, and follow-up without calling tools.
---

# Submit an Employee Request

## Intent: employee-helpdesk-submit-help
### User request patterns
- how do I submit an HR request
- submit a salary certificate request
- what information is needed for an employee request
- can I attach a file to my HR request
- explain request submission

### Retrieval tags
- employee-helpdesk
- submit
- attachments
- direct-answer

### Answer objective
Explain the employee submission flow and its validation rules.

### Instructions
- Answer directly without calling executable tools.
- Do not claim a request was submitted; use the executable submit leaf when the user is ready to perform the action.

### Direct answer
Open [Employee Helpdesk]({{employee_helpdesk_url}}), choose an active request type, complete its fields, upload any requested files, review the answers, and submit. The request receives a human-readable ticket number and enters the HR workflow. Required fields and attachment limits come from the selected request type, so incomplete answers or unfinished uploads must be corrected before submission.
