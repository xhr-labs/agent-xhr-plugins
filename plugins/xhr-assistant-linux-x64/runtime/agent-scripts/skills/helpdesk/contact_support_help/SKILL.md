---
name: helpdesk-contact-support-help
description: Answer direct HelpDesk FAQ questions about contact support help in X-HR. Use when the user asks these HelpDesk questions without requesting live tool execution.
---

# Contact Support Help

Use this direct-answer leaf when the user asks about contact support help.

# Intent Map

## Intent: helpdesk-contact-support-help
### User request patterns
- How to contact support or send a request for help with an issue?
- What if I need help or have questions?

### Retrieval tags
- helpdesk
- support
- help
- direct-answer

### Answer objective
Answer directly with the documented HelpDesk guidance.

### Instructions
- Answer directly in text using the guidance below.
- Do not call executable tools for this skill.

### Direct answer
1. Open [Support]({{support_url}}), or select it from the bottom of the left navigation.
2. Create a support ticket.
3. Select the appropriate **Topic**, then fill in the **Subject** and **Description** of your issue.
4. Your email is auto-filled, but you can review or update it if needed.
5. (Optional) Attach screenshots or documents — files up to 5MB are supported (PDF, DOC, DOCX, JPG, PNG).
6. Click **Submit**.

**Alternative way**: ask Agent to submit it directly for you e.g *"Submit a support ticket for me"*

**Prerequisites**
- Users must be logged in.
- No special role required — all users can submit support requests.

**Common Errors and Solutions**
- **Form not loading**: Try refreshing the page or clearing your cache.
- **Submit button disabled**: Ensure all required fields (topic, subject, description) are filled in.
