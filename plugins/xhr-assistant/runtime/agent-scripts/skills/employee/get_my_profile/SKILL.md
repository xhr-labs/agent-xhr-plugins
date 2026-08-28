---
name: employee-get-my-profile
description: Get the current authenticated user's employee profile. Use when the user asks for their own live profile details, wants to identify the current authenticated user, or the workflow needs current-user profile data before a later employee-scoped action.
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

### Retrieval tags
- employee
- profile
- current-user
- me
- authenticated-user
- live-data

### Answer objective
Return the current authenticated user's live profile.

### Instructions
- Use this leaf only for the current authenticated user.
- Use it when the user wants live profile data about themselves.
- Do not use it to search for another employee.
- Do not use it for how-to/profile-edit guidance; use the direct-answer employee help leaves for FAQ/help questions.
- If the user is asking about another person, use employee search flows instead.
- Keep the response grounded in the authenticated user context returned by the backend.

### Execution
- Run the current-profile script via the restricted command-style exec surface:

```text
python skills/employee/get_my_profile/scripts/get_my_profile.py
```