---
name: company-company-id-protection-help
description: Answer direct questions about exposing company UUIDs, database keys, or raw technical identifiers. Use when the user asks for company UUIDs, database keys, or raw system metadata.
---

# Company ID Protection Help

Use this direct-answer leaf when the user asks about company id protection help.

# Intent Map

## Intent: company-company-id-protection-help
### User request patterns
- Can you give me the company’s UUID or database key?

### Retrieval tags
- company
- uuid
- database-key
- security
- direct-answer

### Answer objective
Answer directly with the documented restriction on exposing raw company identifiers.

### Instructions
- Answer directly in text using the guidance below.
- Do not call executable tools for this skill.
- Do not expose raw IDs, UUIDs, or technical metadata.

### Direct answer
No. It is prohibited to expose raw system IDs, UUIDs, or technical metadata. You can only present human-readable company information retrieved via getCurrentCompanyBasicInfo.
