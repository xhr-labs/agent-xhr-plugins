---
name: search-company-document
description: Search company documents by natural-language query. Use when the user wants to search company documents by topic, keyword, or phrase instead of listing all documents, and the agent should execute the runtime script at skills/documents/search_company_document/scripts/search_company_document.py.
---

# Search company document

Use this executable/search leaf when the user wants to search company documents by query rather than list all documents.

## Runtime entrypoint
- Execute `skills/documents/search_company_document/scripts/search_company_document.py`.
- Do not search for another child skill under this directory.

# Intent Map

## Intent: search-company-document
### User request patterns
- document
- search document
- search

### Retrieval tags
- documents
- search
- company-documents

### Answer objective
Search company documents by query and return the matching results relevant to the user's requested topic.

### Instructions
- Treat this as a search leaf, not a list leaf.
- Use this skill when the user wants discovery by keyword or topic.
- Keep the user query visible and pass it directly to the search script as `--query`.
- Always pass `--source company_document`; this leaf searches company documents only.
- If the user query is too vague, ask a short clarification question before running the tool.
- Do not invent search results.
- If the search returns no matching results, tell the user clearly that no matching company documents were found.

### Execution
```text
python skills/documents/search_company_document/scripts/search_company_document.py --query "<user query>" --source company_document
```
