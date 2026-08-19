---
name: add-employee-help
description: Answer direct how-to questions about adding a new employee in X-HR. Use when the user asks how to invite or create a new employee without requesting live employee actions.
---

# Add Employee Help

Use this direct-answer leaf when the user asks how to add a new employee.

# Intent Map

## Intent: add-employee-help
### User request patterns
- How to add a new employee
- How do I invite a new user

### Retrieval tags
- employee
- add-employee
- onboarding
- direct-answer

### Answer objective
Answer directly with the documented employee creation steps.

### Instructions
- Answer directly in text using the guidance below.
- Do not call executable tools for this skill.

### Direct answer
1. Go to [People → Add Employee]({{add_employee_url}}).
2. **Fill Out Personal Information**
   - Select **Work Location**.
   - Enter details such as full name, contact information, date of birth, and other personal data.
3. **Enter Job Details**
   - Job title
   - Department
   - Employment type (Full-time, Part-time, Contract)
   - Start date
   - Manager
4. **Set Compensation Details**
   - Salary
   - Benefits
   - Payment information (if applicable)
5. **Upload Documents**
   - Attach or request the employee to upload necessary files such as ID proof, resume, or contracts.
6. **Review and Submit**
   - Double-check all entered information for accuracy.
7. **Send Activation Email**
   - Choose whether an activation link should be sent immediately.
8. **Complete Onboarding**
   - The employee can complete assigned onboarding forms and tasks after activation.

For multiple employees, use the People bulk import flow to download a work-location template, map CSV columns, review invalid rows, include compliance or custom fields, and choose activation-link behavior.

When HR starts from a public onboarding submission, recognized answers can prefill the Add Employee form. Accepted dependents can be created with the new employee record.

**Prerequisites**
- User must have **Admin** role or **Edit** access for "Add Employees" under **Access Control**.

**Common Errors and Solutions**
- **Email already exists**: Check if the employee was previously added or use a different email.
- **Manager not found**: Verify that the manager is active/added in the system.
- **Missing fields**: Check work-location-specific custom, contact-address, and compliance fields. Use an onboarding form when the employee should provide the information.
- **Other undefined errors**: Click **Support** (in the navigation drawer) and let us know.

Check out the [video](https://youtu.be/62td5sMtlmA) for more details.
