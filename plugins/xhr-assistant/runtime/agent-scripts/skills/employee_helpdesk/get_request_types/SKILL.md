---
name: employee-helpdesk-get-request-types
description: List active Employee Helpdesk request types available to the authenticated employee.
side_effect: read
---

# Get Employee Request Types

## Intent: employee-helpdesk-get-request-types
### User request patterns
- list my available HR request types
- show Employee Helpdesk request types
- find the request type id for salary certificate
- what HR requests can I submit

### Retrieval tags
- employee-helpdesk
- request-types
- list
- read-action

### Answer objective
Retrieve active request types and their current versions for employee submission.

### Instructions
- Use this before submission when the user supplied a type name but not its ID.
- Do not claim a type is available until it appears in the response; when the call fails, say the catalog could not be loaded instead of listing examples.
- The list has no form fields. Read `get_request_type --request-type-id <id>` before collecting answers.
- Follow `meta.next_cursor` verbatim; when it is null there is no next page. Never construct a cursor.

### Arguments
- `locale` (optional)
- `cursor` (optional)
- `page_size` (optional)

### Execution
`python skills/employee_helpdesk/get_request_types/scripts/get_request_types.py [--locale <locale>] [--cursor <cursor>] [--page-size <n>]`
