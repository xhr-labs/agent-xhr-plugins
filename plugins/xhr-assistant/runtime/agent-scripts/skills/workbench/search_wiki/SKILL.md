---
name: workbench-search-wiki
description: Search Workbench wiki and space documents by natural-language query. Use when the user asks to search wiki content, search space documents, find a document in a project or space wiki, or discover pages by keyword instead of opening a known page directly, and the agent should execute the runtime script at skills/documents/search_company_document/scripts/search_company_document.py.
---

# Search Wiki

Use this executable/search leaf when the user wants to search wiki or space documents by query rather than fetch a known page directly.

## Runtime entrypoint
- Execute `skills/documents/search_company_document/scripts/search_company_document.py`.
- Do not search for another child skill under this directory.

# Intent Map

## Intent: search-wiki
### User request patterns
- search wiki
- search the wiki for leave policy
- search space document about onboarding
- find a wiki page about payroll
- search project wiki for release flow
- search documents in the space wiki
- look up a space document about API conventions
- find wiki content related to time off
- search company wiki for approval policy
- search wiki articles about attendance
- please help summarize the actionables that has priority = P1
- please help summarize page then create task with action which has priority = P1
- please help summarize wiki page

### Retrieval tags
- workbench
- wiki
- search
- documents
- space-documents
- project-wiki
- company-wiki

### Answer objective
Search wiki documents by query and return the search results relevant to the user's requested topic.

### Instructions
- Treat this as a search leaf, not a page-fetch leaf.
- Use this skill when the user wants discovery by keyword or topic, not when the exact page is already known.
- Do not invent search results.
- Keep the user query visible and pass it directly to the search script as `--query`.
- Always pass `--source wiki`; this leaf searches Workbench wiki documents only.
- If the user query is too vague, ask a short clarification question to improve the search query before running the tool.
- If the search returns no matching results, tell the user clearly that no matching wiki documents were found.

### Execution
```text
python skills/workbench/search_wiki/scripts/search_wiki.py --query "<user query>"
```
