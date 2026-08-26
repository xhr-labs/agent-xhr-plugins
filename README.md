# xHR Assistant

Bring xHR into your AI assistant. xHR Assistant is a plugin for
**Claude Code**, **OpenAI Codex**, and **Google Antigravity** that lets the
assistant securely work with your xHR workspace — check leave balances,
submit time off, manage timesheets and shifts, look up employees and company
documents, run Workbench projects, and much more — all through natural
conversation.

Your access token stays in your operating system's secure credential store.
It is never shared with the AI assistant or typed into chat.

## 1. Install (Cross-platform)

### Claude Code
```bash
claude plugin marketplace add https://github.com/xhr-labs/agent-xhr-plugins
claude plugin install xhr-assistant@xhr
```

### OpenAI Codex
```bash
codex plugin marketplace add https://github.com/xhr-labs/agent-xhr-plugins
codex plugin add xhr-assistant@xhr
```

### Google Antigravity (IDE or agy CLI)
```bash
# Windows
git clone --depth 1 https://github.com/xhr-labs/agent-xhr-plugins
agent-xhr-plugins\plugins\xhr-assistant\bin\xhr-assistant.exe install antigravity

# macOS / Linux
git clone --depth 1 https://github.com/xhr-labs/agent-xhr-plugins
./agent-xhr-plugins/plugins/xhr-assistant/bin/xhr-assistant install antigravity
```

After installing, **restart your assistant** (or start a new session) so the
xHR skills and tools load.

## 3. Sign in (first use)

1. Ask your assistant something xHR-related, e.g. *"Show my leave balance."*
2. A private xHR sign-in window opens. Generate an access token in
   **xHR Platform** and paste it there.
3. Retry your request — done.

If no window can open (for example over SSH), the assistant shows you a
one-line `auth token` command to run in your terminal instead. Sign in once
per machine: every supported assistant on the same computer shares it.
Tokens expire after one hour; when that happens, the assistant simply asks
you to sign in again.

## 4. Switch environment (optional)

The plugin talks to xHR production by default. To use another environment,
run the bundled program once, then start a new session and sign in with a
token from that environment:

```powershell
# Windows, installed via Claude Code — adjust the path for your host/platform
& "$env:USERPROFILE\.claude\plugins\cache\xhr\xhr-assistant\<version>\bin\xhr-assistant.exe" config set-env sandbox
```

```bash
# macOS / Linux
~/.claude/plugins/cache/xhr/xhr-assistant/<version>/bin/xhr-assistant config set-env sandbox
```

Available environments: `prod` (default), `sandbox`, `dev` — or
`config set-url <url>` for a custom address, and `config show` to check the
current one. The setting applies to every assistant on your machine.

Installed through Codex? The program lives under
`~/.codex/plugins/cache/...` instead. Through Antigravity? It is inside the
folder you cloned or extracted.

## 5. Update

New releases land on the same branches, so updating is:

```bash
# Claude Code
claude plugin marketplace update xhr
claude plugin update xhr-assistant@xhr
```

```bash
# Codex
codex plugin marketplace upgrade xhr
codex plugin add xhr-assistant@xhr
```

```bash
# Antigravity — pull the clone, then re-run the installer
git -C agent-xhr-plugins pull
agent-xhr-plugins/plugins/xhr-assistant/bin/xhr-assistant.exe install antigravity
```

Restart your assistant afterwards.

## Uninstall

```bash
# Claude Code
claude plugin uninstall xhr-assistant@xhr
claude plugin marketplace remove xhr
```

```bash
# Codex
codex plugin remove xhr-assistant@xhr
codex plugin marketplace remove xhr
```

```bash
# Antigravity
agent-xhr-plugins/plugins/xhr-assistant/bin/xhr-assistant uninstall antigravity
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `Source path does not exist` when installing | The branch is missing from the marketplace address — make sure it ends with your `release/...` branch. |
| `file not found` running the program on macOS/Linux | Use `bin/xhr-assistant` — there is no `.exe` outside Windows. |
| macOS refuses to run the program | Run `codesign --force -s - <path-to-binary>` once, then retry. |
| The assistant says authentication is required | Your token expired (they last one hour) or belongs to a different environment — sign in again. |
| Skills or tools don't appear | Restart the assistant or start a new session after installing. |

Need help? Ask your assistant to *"submit an xHR support ticket"* — that
works through this plugin too. 😉
