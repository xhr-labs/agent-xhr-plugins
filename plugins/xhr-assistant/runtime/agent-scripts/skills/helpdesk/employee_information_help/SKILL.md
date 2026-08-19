---
name: helpdesk-employee-information-help
description: Answer direct HelpDesk FAQ questions about employee information help in X-HR. Use when the user asks these HelpDesk questions without requesting live tool execution.
---

# Employee Information Help

Use this direct-answer leaf when the user asks about employee information help.

# Intent Map

## Intent: helpdesk-employee-information-help
### User request patterns
- How to get employee information (email, team, position, manager, department)?

### Retrieval tags
- helpdesk
- employee-information
- people
- direct-answer

### Answer objective
Answer directly with the documented HelpDesk guidance.

### Instructions
- Answer directly in text using the guidance below.
- Do not call executable tools for this skill.

### Direct answer
**Instructions:**
1. Go to [People]({{people_url}})
2. Search for employee by name or ID
3. Select your desired information from the available information (email, team, position, manager, organization, department)

**Prerequisites:** note that only the information listed above should be available for employees, all other information is available only for administrators

**Common Errors & Solutions:**
- "Employee not found" → Verify user is active/added in the system
- “Unable to see information” -> Check if you have the right permissions for this action
