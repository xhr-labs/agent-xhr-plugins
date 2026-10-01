---
name: language-change-language
description: Change the platform language after first fetching the supported language list. Use when the user explicitly asks to switch or change the platform language, for example to Vietnamese, German, or another supported language.
---

# Change language

Use this skill only when the user explicitly requests a platform or UI language change.
If the user is only asking the assistant to chat, speak, or reply in a language, do not change the platform language.
In that case, simply confirm that you will continue the conversation in the requested language from the next turns onward.

# Intent Map

## Intent: change-language
### User request patterns
- Switch/Change platform to Language (for example Vietnamese)
- change platform language
- change UI language
- switch the app to Vietnamese
- đổi ngôn ngữ giao diện
- đổi ngôn ngữ hệ thống
- change language

### Retrieval tags
- language
- localization
- switch-language
- change-language
- supported-languages
- platform-language
- ui-language

### Conversation-language examples (do not execute tools)
- please chat with me in Vietnamese
- speak Vietnamese with me
- from now on reply in German
- hãy nói chuyện với tôi bằng tiếng Việt
- trả lời tôi bằng tiếng Anh

### Answer objective
Handle explicit platform language change requests by first fetching supported languages and then changing the language without adding unrelated explanatory text.

### Instructions
- This workflow applies only when the user explicitly requests a platform or UI language change, such as switching the app to German or changing the platform language to Vietnamese.
- Treat an explicit platform-language change request in the current user turn as an execution request, not as a request to summarize prior actions.
- If the user is asking to change the platform language now, always execute the workflow in this turn. Do not satisfy the request by citing conversation history, prior assistant messages, or earlier tool results alone.
- Never assume the platform language has already been changed just because the conversation history mentions the same language or a prior request to change it.
- Do not answer a fresh change-language request with a confirmation like "already changed" or "done" unless you executed the required tool steps for this request in the current turn.
- If the user only asks the assistant to chat, speak, or reply in a language, treat that as a conversation-language preference, not a platform-language change.
- For conversation-language preference requests, do not call any tool. Just confirm briefly that you will continue in the requested language from the next turns onward.
- Do not treat normal user messages as platform-language-change requests.
- Do not explain UI settings in place of the workflow.
- Before any platform language change action, you must fetch the supported language list first.
- Do not output normal user-facing text before the supported-language lookup and the language-change action are both completed.
- After receiving the supported language list, call the language-change action as the first functional follow-up.
- Only use languages that are present in the supported-language response.
- If the requested language is unsupported, say so clearly after the supported-language lookup completes.
- After a successful change-language tool result, return the tool-confirmed result and stop. Do not rely on older history to form the confirmation.

### Execution
- First run the supported-language lookup:
  - `get_supported_languages {}`
- Then run the language-change action with the requested supported language:
  - `change_language {"language": "<requested supported language>"}`
