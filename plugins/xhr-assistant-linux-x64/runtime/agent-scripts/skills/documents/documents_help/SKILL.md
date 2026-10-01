---
name: documents-help
description: Answer direct how-to questions about uploading company documents in X-HR. Use when the user asks how to add or upload company documents without requesting live document actions.
---

# Documents Help

Use this direct-answer leaf when the user asks how to upload company documents.

# Intent Map

## Intent: documents-help
### User request patterns
- how to add or upload company documents?

### Retrieval tags
- documents
- documents
- upload
- direct-answer

### Answer objective
Answer directly with the documented steps for uploading company documents.

### Instructions
- Answer directly in text using the guidance below.
- Do not call executable tools for this skill.

### Direct answer
**Instructions:**
1. Go to [Documents]({{documents_url}}) -> "Upload Document"
2. Select or create a category and manage document access.
3. Upload file (ensure it meets the size and format requirements).
4. Check “Enable AI agent access” for documents you want our agent to be able to use and share with employees (e.g. timeoff policy, onboarding guide, company values etc)
5. Edit document permissions to determine who has access to it 
Prerequisites: User must have Admin access to Documents

**Common Errors & Solutions:**
- **Document upload failed**: Check the file restrictions shown in the upload dialog and verify the company's storage allowance. Limits can vary by document flow and plan.
- "Category not found" → Create new category first or select from existing options
- "Permission error" → Ensure you have document management rights

Check out the [video](https://youtu.be/vKBwqXrMsp8?si=LEK2YlnCFWeGLD7A) for more details.
