---
name: workbench-share-and-permissions
description: Answer direct how-to questions about sharing Workbench spaces or projects, involving members, and setting permissions. Use when the user asks how to add members, share a space or project, or manage access roles in Workbench.
---

# Share and Permissions

Use this direct-answer leaf when the user asks how to add members to a Workbench space or project or how to manage sharing permissions.

# Intent Map

## Intent: explain-workbench-sharing-and-permissions
### User request patterns
- How to involve a member to a space
- How to involve a member to a project
- How to set permission for a space
- How to set permission for a project
- explain why Owner is missing from the Share role dropdown
- explain who can create sprints in a Workbench space

### Retrieval tags
- workbench
- share
- permissions
- member-access
- direct-answer

### Answer objective
Answer directly with the documented Workbench sharing and permission steps, without calling executable tools.

### Instructions
- Answer directly in text using the guidance below.
- Do not call executable tools for this skill.
- Use the documented steps and notes exactly as written unless the user asks for clarification.
- If the user asks for a live action or system state instead of a how-to explanation, switch to a more appropriate executable skill rather than inventing data.

### Direct answer
## How to Involve a Team Member in a private Space

To add a team member to a space or project you’re working on, follow these steps:

1. Go to the **Space Details** page.  
2. Click the **Share** button in the top-right corner of the screen.  
3. Search for the member you want to add to the space.

## Notes
- You can search for members by **department**, **team**, or **job title**.  
- The Share role dropdown offers **Contributor** and **Viewer**:
  - **Contributor** can manage tasks within the space.
  - **Viewer** can view space information.
- **Owner** is an existing space role, displayed as a badge for the owner; it is not an option in the Share role dropdown. Do not instruct users to select Owner when inviting a member or changing a collaborator's role.
- Sprint management in the current Workbench UI requires the space Owner, and sprint planning must be enabled for the space. Contributor access does not grant sprint management.
- If a user cannot find Owner while trying to let a colleague create sprints, explain that this is expected for the Share dropdown and ask the current Owner to create/manage the sprint. Do not suggest refreshing, upgrading access, or selecting a different share role to make Owner appear.
- Do not invent a transfer-ownership menu or suggest assigning Owner through an API/tool as a workaround. If ownership delegation is required, explain that this Share flow does not support it and direct the user to support to confirm available options; do not promise a transfer capability.
