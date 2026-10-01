---
name: update-employee-help
description: Answer direct how-to questions about updating or editing employee information in X-HR. Use when the user asks how to edit an employee profile without requesting live employee actions.
---

# Update Employee Help

Use this direct-answer leaf when the user asks how to update or edit employee information.

# Intent Map

## Intent: update-employee-help
### User request patterns
- How to update/edit/change an employee info?

### Retrieval tags
- employee
- update-employee
- edit-profile
- direct-answer

### Answer objective
Answer directly with the documented employee update steps.

### Instructions
- Answer directly in text using the guidance below.
- Do not call executable tools for this skill.

### Direct answer
**Update partially**

1. Go to [People]({{people_url}}).
2. Search for the employee by name or ID.
3. Click on the employee name to open their profile.
4. Select the desired profile section (Personal, Job, Compensation, etc.).
5. Update required fields directly in-line or select **Edit** from the available options.

**Update full on 1 form**

1. Go to [People]({{people_url}})
2. Search for the employee by name or ID.
3. Click on the 3 dots icon on the right side of the row
4. Click on Edit action 

**Prerequisites**
- User must have **Admin** role or **Edit** access for the specific data block (profile section).

**Common Errors and Solutions**
- **Only able to see employee Summary**: Check if you have edit permissions for this employee.
- **Required field missing**: Check if you have edit permissions for this employee.

**Next Steps / Follow-Up Suggestions**
- Use the **Document and Policy Management** features so new employees can easily find company information and be assisted by the smart agent more effectively.
- Explore other contextual suggestions to enhance the employee profile management experience.
