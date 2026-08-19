---
name: helpdesk-rebac-and-roles-help
description: Answer direct HelpDesk FAQ questions about rebac and roles help in X-HR. Use when the user asks these HelpDesk questions without requesting live tool execution.
---

# ReBAC and Roles Help

Use this direct-answer leaf when the user asks about rebac and roles help.

# Intent Map

## Intent: helpdesk-rebac-and-roles-help
### User request patterns
- How to set up relationship-based access control (ReBAC) and configure roles, permissions, and organization structure?
- How to configure access permissions and roles in the organization?
- How to setup ReBAC

### Retrieval tags
- helpdesk
- rebac
- roles
- permissions
- direct-answer

### Answer objective
Answer directly with the documented HelpDesk guidance.

### Instructions
- Answer directly in text using the guidance below.
- Do not call executable tools for this skill.

### Direct answer
1. Go to [Workspace → Access & Permissions]({{access_permissions_url}}).

2. In **Organization & Roles**, click **Change Structure** and choose:
   - **Flat Structure** – for small teams (<30). Roles only at org level (Admin, HR Manager, Employee).
   - **Team & Department** – for larger organizations. Adds Departments & Teams with roles like Dept. Lead, Dept. HR, Team Lead, Team Member.

3. If using **Team & Department**:
   - Click **+ Add** to create groups (e.g., Product, Marketing, HR, IT).
   - Use **Edit & Assign** to add people and assign roles (Lead, HR Partner, Member).
   - Review and adjust Organization-level roles (Admin, HR Manager, Employee).

4. Switch to the **Permissions** tab:
   - For each product area (Employee Database, Company Documents, etc.), set access per section or row.
   - Select which roles/groups can view, edit, or manage each section.
   - Combine Org-level roles (HR Manager, All Employees) with Dept/Team roles (Dept. Lead, Team Member).
   - For installed apps, also review each app's **App Permission** page when available. Many micro-apps separate app access from data-block permissions.

5. Suggested baseline setup:
   - **Summary** → All employees
   - **Personal Information** → HR Manager (+ Dept. HR if applicable)
   - **Job** → Dept. Lead / Team Lead
   - **Compensation** → HR Manager (+ Dept. Lead if allowed)
   - **Documents** → HR Manager (+ Dept. HR optional)
   - **Roles** → Owner/Admin only

6. For larger organizations, review delegated roles such as **Deputy Department Head** where available. These roles can support department-level visibility or approvals without granting broad owner/admin access.

**Prerequisites**
- User must have **Admin** role to access **Access & Permissions**.
- Must select an organization structure (Flat or Team & Department) before assigning detailed permissions.

**Common Errors and Solutions**
- **Permission denied**: Verify that you’re logged in as Admin.
- **Cannot assign role**: Ensure the organization structure is selected before assigning.
- **Data not visible**: Confirm that the role has view rights under Permissions.
- **Too many overlapping roles**: Remove duplicate or conflicting assignments.
- **App installed but page hidden**: Check both workspace access and the app-specific App Permission page.

Check out the [video](https://youtu.be/cN9DYncszvA?si=rSEuSbgft8orzCcN) for more details.
