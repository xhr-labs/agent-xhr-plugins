# xHR Assistant

Bring xHR into your AI assistant. xHR Assistant is a plugin for
**Claude Code**, **OpenAI Codex**, and **Google Antigravity** that lets the
assistant securely work with your xHR workspace — check leave balances,
submit time off, manage timesheets and shifts, look up employees and company
documents, run Workbench projects, and much more — all through natural
conversation.

Your access token stays in your operating system's secure credential store.
It is never shared with the AI assistant or typed into chat.

## 1. Pick the plugin for your operating system

The marketplace ships one plugin per platform. Install **only** the one that
matches your machine:

| Your machine | Plugin name |
|---|---|
| Windows (x64) | `xhr-assistant` |
| macOS (Apple Silicon) | `xhr-assistant-macos` |
| Linux (x64) | `xhr-assistant-linux-x64` |
| Linux (arm64) | `xhr-assistant-linux-arm64` |

The commands below use `<plugin>` as a placeholder — substitute the name from
the table.

## 2. Install

### Claude Code
```bash
claude plugin marketplace add https://github.com/xhr-labs/agent-xhr-plugins
claude plugin install <plugin>@xhr        # e.g. xhr-assistant-macos@xhr on a Mac
```

### OpenAI Codex
```bash
codex plugin marketplace add https://github.com/xhr-labs/agent-xhr-plugins
codex plugin add <plugin>@xhr             # e.g. xhr-assistant@xhr on Windows
```

### Google Antigravity (IDE or agy CLI)
```bash
# Windows
git clone --depth 1 https://github.com/xhr-labs/agent-xhr-plugins
agent-xhr-plugins\plugins\xhr-assistant\bin\xhr-assistant.exe install antigravity

# macOS (Apple Silicon)
git clone --depth 1 https://github.com/xhr-labs/agent-xhr-plugins
./agent-xhr-plugins/plugins/xhr-assistant-macos/bin/xhr-assistant install antigravity

# Linux: use plugins/xhr-assistant-linux-x64 or plugins/xhr-assistant-linux-arm64
```

After installing, **restart your assistant** (or start a new session) so the
xHR skills and tools load. The first xHR request downloads the plugin's
Python runtime automatically (one time, needs network access).

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
# macOS / Linux — the cache folder is named after your plugin
~/.claude/plugins/cache/xhr/xhr-assistant-macos/<version>/bin/xhr-assistant config set-env sandbox
```

Available environments: `prod` (default), `sandbox`, `dev` — or
`config set-url <url>` for a custom address, and `config show` to check the
current one. The setting applies to every assistant on your machine.

Installed through Codex? The program lives under
`~/.codex/plugins/cache/...` instead. Through Antigravity? It is inside the
folder you cloned or extracted.

## 5. Update

New releases land on `main`, so updating is:

```bash
# Claude Code
claude plugin marketplace update xhr
claude plugin update <plugin>@xhr
```

```bash
# Codex
codex plugin marketplace upgrade xhr
codex plugin add <plugin>@xhr
```

```bash
# Antigravity — pull the clone, then re-run the installer from your OS folder
git -C agent-xhr-plugins pull
agent-xhr-plugins/plugins/xhr-assistant/bin/xhr-assistant.exe install antigravity
```

Restart your assistant afterwards.

> Upgrading from a version before 0.2.0 on macOS or Linux? Those installs
> were broken by a packaging bug (they carried a Windows launcher). Remove
> the old `xhr-assistant` plugin and install the plugin for your OS from the
> table above.

## Uninstall

```bash
# Claude Code
claude plugin uninstall <plugin>@xhr
claude plugin marketplace remove xhr
```

```bash
# Codex
codex plugin remove <plugin>@xhr
codex plugin marketplace remove xhr
```

```bash
# Antigravity
agent-xhr-plugins/plugins/<plugin>/bin/xhr-assistant uninstall antigravity
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `MCP startup failed: No such file or directory` | You installed a plugin built for a different operating system — uninstall it and install the one from the table above. |
| `file not found` running the program on macOS/Linux | Use `bin/xhr-assistant` — there is no `.exe` outside Windows. |
| macOS refuses to run the program | Run `codesign --force -s - <path-to-binary>` once, then retry. |
| First request fails mentioning the Python runtime | The one-time runtime download needs network access — check your connection and retry, or run `bin/xhr-assistant setup`. |
| The assistant says authentication is required | Your token expired (they last one hour) or belongs to a different environment — sign in again. |
| Skills or tools don't appear | Restart the assistant or start a new session after installing. |

Need help? Ask your assistant to *"submit an xHR support ticket"* — that
works through this plugin too. 😉
