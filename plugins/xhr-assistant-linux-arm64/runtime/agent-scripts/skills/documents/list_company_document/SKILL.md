---
name: list-company-document
description: List company documents for the current workspace. Use when the user wants to view or list company documents and the agent should execute the runtime script at skills/documents/list_company_document/scripts/list_company_documents.py.
---

# List company document

Use this executable/search leaf when the user wants to list company documents rather than search by query.

# Intent Map

## Intent: list-company-document
### User request patterns
- view my company document
- my company document
- list document

### Retrieval tags
- documents
- list
- company-documents

### Answer objective
List company documents available to the current user and return the results from the underlying document listing tool.

### Instructions
- Treat this as a list leaf, not a search leaf.
- Use this skill when the user wants to browse or view company documents without a specific search keyword.
- Do not invent document names, categories, or permissions.
- If the user gives extra narrowing filters later, pass them only when the underlying tool supports them.
- If the list returns no matching results, tell the user clearly that no company documents were found.

### Execution
```text
python skills/documents/list_company_document/scripts/list_company_documents.py
```
