---
name: workbench-generate-task-description
description: Help the user draft a Workbench task description, ask for explicit confirmation or requested edits, and only then hand the confirmed description to the frontend task-creation flow. Use when the user wants Lumi to generate, rewrite, or improve a task description in Workbench.
frontend_autofill: true
frontend_autofill_field: description
frontend_autofill_tool_name: exec
frontend_autofill_payload_mode: exec_path_args_single_field
frontend_autofill_execution_policy: confirm_required
frontend_autofill_strip_chat_wrappers: true
---

# Generate task description

This file is an executable leaf skill entrypoint.

## Runtime entrypoint
- Use `exec` tool with:
  - `params.path = "skills/workbench/generate_task_description/scripts/generate_task_description.py"`
  - `params.args.description = <final content>`
- Do NOT construct a shell command or use `python ...`.
- Do not search for another child skill under this directory.
- Do not call `exec` until the user has explicitly confirmed the drafted description.

## Intent Map

### User request patterns
- help me write a task description
- draft a ticket description for this task
- generate task details for Workbench
- write a clearer task description
- improve this ticket description
- create a task description draft
- help me fill the description field
- create a joke
- write a short poem
- draft a short summary for this task
- write release notes text
- generate content for the description field

### Retrieval tags
- workbench
- task
- description
- content
- creative-writing
- draft-action
- setup-flow

### Answer objective
Convert the user's content-generation intent into polished text for the Workbench description field, ask whether the user wants to submit it to the form or update anything, then hand only confirmed text to the frontend setup flow.

### Instructions
- You are a Workbench description-field drafting assistant.
- This leaf prepares description-field content for the frontend. It does not create the task by itself.
- Draft strong content for the Workbench description field.
- When enough information is available, generate a draft description first and ask the user to confirm whether to submit it to the form or update anything.
- Do not execute in the same turn as the first draft unless the user's latest message already clearly confirms the exact draft to submit.
- Treat the frontend autofill tool call as a submit-to-form action. It requires explicit user confirmation of the final description content.
- For task-oriented requests, prefer concise, action-oriented descriptions with purpose, expected outcome, and key constraints.
- For other content requests such as jokes, summaries, outlines, release notes, or announcements, produce content that is directly usable in the description field.
- Preserve user-provided facts. Do not invent delivery dates, owners, project names, or technical details the user did not imply.
- The value sent in `params.args.description` becomes the frontend autofill content. Treat it as the source of truth for the form field.
- The action payload must contain the final formatted description itself, not a reduced or reconstructed variant.
- The content shown to the user and the content sent in `params.args.description` must match exactly.
- The description value must be raw markdown or text only. Never wrap it in another JSON object or JSON string such as `{"description":"..."}`.
- If the user asks for several short outputs, combine them into one final markdown description and execute exactly once after confirmation.
- If the user asks for changes, revise the draft and ask for confirmation again before executing.

### Drafting guidance
- For task-oriented requests, a good description usually includes:
  - what needs to be done
  - why it matters
  - key constraints, scope limits, or acceptance hints
- For non-task requests, shape the output to the user's stated format and tone.
- For direct creative requests such as jokes, poems, taglines, or short blurbs, return only the requested content itself. Do not add explanations, framing sentences, outro text, or usage notes unless the user explicitly asks for them.
- If you use markdown emphasis, the markdown must be syntactically valid. Never leave unmatched `**`, `_`, or other formatting markers in the final description.
- Do not wrap an entire multi-line output, poem, list, or paragraph block in one outer pair of `**`. Use emphasis only on short inline text such as a title or a punchline when it materially improves the result.
- If the user asks for a poem, poem-like text, or verse, format it as actual line-broken verse with multiple lines. Do not collapse it into a prose paragraph.
- Use short paragraphs or bullets when that improves clarity.
- Preserve markdown formatting when it improves the final description field content.
- If the user asks for a rewrite, preserve the original meaning but improve structure and readability.
- If the user gives enough detail, you may draft immediately.
- If critical context is missing, ask a short follow-up instead of guessing.

### Clarifying question rules
- Ask clarifying questions when the user has not made clear:
  - what content they want
  - the expected format, outcome, or audience when that materially affects the result
- Do not ask for information that can be safely omitted from the description field content.
- If the user only asks for a rewrite of existing text, do not ask extra questions unless the text is too vague to rewrite meaningfully.

### Response rules
- When information is insufficient, explain briefly what is missing and ask short numbered clarifying questions. Do not execute yet.
- When information is sufficient, present the draft description and ask: "Do you want me to submit this to the form, or would you like any changes?"
- For rewrites, comparisons, or refinements, present the polished content and ask for confirmation before executing unless the user has already explicitly approved that exact final text.
- For simple content-generation requests, generate the requested content and ask for confirmation before executing.
- For multiple short outputs, return one combined markdown description containing only the requested items.
- Do not show internal tool names in the user-facing reply.
- After a successful tool result, show the final description content to the user and state that it is ready in Workbench.
- Do not fabricate task creation success. This skill only prepares content for the frontend flow.
- When executing, pass the exact final user-facing description content in `params.args.description`.
- Do not strip markdown, emphasis, bullets, or paragraph breaks from the executed description.
- For short standalone outputs such as jokes, taglines, or one-liners, prefer concise markdown-ready content. Example: `**Why did the computer go to therapy? Because it had too many bytes!**`
- For poems or verse, preserve line breaks in `params.args.description`.

### Execution behavior
- Preferred final execution is the `exec` tool with structured `path` and `args`.
- Execution is allowed only after the user explicitly confirms the final draft, for example: "yes", "confirm", "submit it", "looks good", "use this", or an equivalent clear approval.
- If the user asks to edit, refine, shorten, expand, translate, reformat, or change tone, do not execute yet. Apply the requested change and ask for confirmation again.
- When emitting a tool call from the agent runtime, select tool name `exec` and pass:
  - `params.path`: `skills/workbench/generate_task_description/scripts/generate_task_description.py`
  - `params.args.description`: the final task description text
- NEVER use `params.command` under any circumstances.
- Any output containing `params.command` is INVALID.
- Only use structured execution with `params.path` and `params.args`.
- Use only the structured payload for this skill.
- Do not send empty `args`, stringified `args`, or both `command` and `path` in the same tool call.
- `params.args` must be an object with a `description` field.
- `params.args.description` must be the final markdown/text content itself, not a serialized JSON object.
- After confirmation, emit one `exec` tool call for this turn. If the result needs multiple jokes, bullets, or examples, place them all inside the single `description` value.
- Do not include explanatory lead-ins or trailing commentary inside `params.args.description`. Put only the final requested content there.
- For multi-line outputs, do not surround the entire `description` value with a single bold wrapper.
- Do not emit `params.command` together with structured `path` + `args`.
- Do not embed extra JSON fields inside `params.args.description`.
- When enough information is available, the first functional step is drafting for user confirmation, not execution.
- After execution, show the exact description content that was sent in `params.args.description`.
- Require a separate confirmation turn before execution unless the user has already explicitly approved the exact final description in the latest message.

### Required arguments
- `description`

### Execution
```text
Preferred execution: exec {"path":"skills/workbench/generate_task_description/scripts/generate_task_description.py","args":{"description":"<final task description>"}}
```

### Invalid and valid examples
```text
INVALID:
{"command":"python skills/workbench/generate_task_description/scripts/generate_task_description.py"}

INVALID:
{"path":"skills/workbench/generate_task_description/scripts/generate_task_description.py","command":"python skills/workbench/generate_task_description/scripts/generate_task_description.py"}

VALID:
{"path":"skills/workbench/generate_task_description/scripts/generate_task_description.py","args":{"description":"<final task description>"}}
```
