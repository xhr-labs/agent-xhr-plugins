---
name: employee-get-my-profile
description: Get the current authenticated user's employee profile. Use when the user asks for their own live profile details, hire date, date of joining, company joining date, wants to identify the current authenticated user, or the workflow needs current-user profile data before a later employee-scoped action.
---

# Get My Profile

Use this executable leaf when the workflow needs the live profile of the current authenticated user.

# Intent Map

## Intent: get-my-profile
### User request patterns
- show my profile
- who am I in the system?
- get my employee profile
- what is my profile info?
- show my account profile
- identify the current user
- show me my profile
- what is my current employee profile?
- get my user profile
- fetch my profile details
- when did I join the company?
- what is my hire date?
- show my date of joining
- I joined the company from 2023
- are you sure? I joined the company from 2023

### Retrieval tags
- employee
- profile
- current-user
- me
- authenticated-user
- live-data
- hire-date
- date-of-joining
- joining-date
- joined-company

### Answer objective
Return the current authenticated user's live profile.

### Instructions
- Use this leaf only for the current authenticated user.
- Use it when the user wants live profile data about themselves, including their hire date or date of joining.
- If the user challenges a payroll, end-of-service, time-off, or eligibility answer by saying they joined on/from a date or year, use this leaf to verify the authenticated user's `date_of_joining` / `hiring_date`.
- Do not use it to search for another employee.
- Do not use it for how-to/profile-edit guidance; use the direct-answer employee help leaves for FAQ/help questions.
- If the user is asking about another person, use employee search flows instead.
- Keep the response grounded in the authenticated user context returned by the backend.

### Execution
- Run the current-profile script via the restricted command-style exec surface:

```text
python skills/employee/get_my_profile/scripts/get_my_profile.py
```
