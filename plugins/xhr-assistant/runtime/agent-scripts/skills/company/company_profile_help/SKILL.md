---
name: company-profile-help
description: Answer direct how-to questions about updating company profile or workspace details in X-HR. Use when the user asks how to edit company information, workspace details, company logo, or basic company settings without requesting live company data.
---

# Company Profile Help

Use this direct-answer leaf when the user asks how to update company profile or workspace details.

# Intent Map

## Intent: company-profile-help
### User request patterns
- How to update company profile or workspace details (logo, name, address)?

### Retrieval tags
- company
- company-profile
- workspace-settings
- logo
- direct-answer

### Answer objective
Answer directly with the documented steps for updating company profile or workspace details.

### Instructions
- Answer directly in text using the guidance below.
- Do not call executable tools for this skill.

### Direct answer
**Instructions:**
1. Go to [Workspace -> Company Account]({{company_account_url}})
2. Upload or update the company logo
3. Click on any row to edit data in-line (e.g., company name, address, email)

**Prerequisites:** User must have Admin role for workspace/company settings

**Common Errors & Solutions:**
- "Permission denied" → Verify that you have edit rights for the workspace
- "Invalid logo format" → Ensure the logo is in a supported format (JPEG, PNG) and under the allowed size
