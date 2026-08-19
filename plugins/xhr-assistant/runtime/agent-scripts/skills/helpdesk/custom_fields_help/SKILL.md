---
name: helpdesk-custom-fields-help
description: Answer direct HelpDesk FAQ questions about custom fields help in X-HR. Use when the user asks these HelpDesk questions without requesting live tool execution.
---

# Custom Fields Help

Use this direct-answer leaf when the user asks about custom fields help.

# Intent Map

## Intent: helpdesk-custom-fields-help
### User request patterns
- How to create and manage custom fields?

### Retrieval tags
- helpdesk
- custom-fields
- workspace
- direct-answer

### Answer objective
Answer directly with the documented HelpDesk guidance.

### Instructions
- Answer directly in text using the guidance below.
- Do not call executable tools for this skill.

### Direct answer
1. Go to [Workspace → Custom Fields]({{custom_fields_url}}).

2. Click **Add New**.

3. Under **Source & Section**, choose **Employee Profile** and the section where the field should appear (e.g., Job Details).

4. In **Visibility & Requirement**:
   - **Active → ON** = field shows in published forms.
   - **Optional → OFF** = required field.
   - **Optional → ON** = nice-to-have field.

5. In **Applied Location**:
   - Keep **Global** for all locations.
   - Or click **+** to target specific locations only.

6. In **Field Setup**:
   - **Type** → Select the input type: Text, Long Text, Select, Date, Person.
   - **Label** → Name the field (e.g., "Probation End Date").
   - If **Select** is chosen → Add dropdown options.

7. The new custom field appears in the list with **Status**, **Applied Location**, **Source & Section**, and **Type**.

8. To use:
   - Open an employee profile (or onboarding flow).
   - Go to the section you assigned (e.g., Job Details).
   - Fill in the field (Date type shows a date picker).
   - Click **Save & Next**.

**Prerequisites**
- User must have **Admin** role to create or edit custom fields.

**Common Errors and Solutions**
- **Field not visible**: Check **Visibility** is set to Active ON.
- **Wrong location**: Verify **Applied Location** is set correctly (Global vs. specific site).
- **Cannot save field**: Ensure a valid **Type** and **Label** are provided.
- **Dropdown empty**: For **Select** type, add at least one option before saving.

Check out the [video](https://youtu.be/Sm8Zz31zb30?si=Mh-GikyqY5j8zEV4) for more details.
