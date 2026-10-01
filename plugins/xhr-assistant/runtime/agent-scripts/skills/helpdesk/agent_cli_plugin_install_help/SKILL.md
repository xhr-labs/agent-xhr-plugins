---
name: helpdesk-agent-cli-plugin-install-help
description: Explain how to install the xHR Assistant plugin for Codex, Claude Code, or Google Antigravity and complete first-use authentication. Use for Agent CLI plugin installation questions, not in-product App Store app installation.
---

# Agent CLI Plugin Installation Help

## Intent: helpdesk-agent-cli-plugin-install-help
### User request patterns
- install the xHR Assistant plugin
- set up xHR Assistant for Codex
- set up xHR Assistant for Claude Code
- connect xHR Assistant to Google Antigravity
- install the xHR plugin for the Agent CLI
- choose the correct plugin for my operating system
- sign in to xHR Assistant for the first time
- why do I need to restart after installing the plugin

### Retrieval tags
- helpdesk
- agent-cli
- xhr-assistant
- plugin
- install
- codex
- claude-code
- antigravity
- agy
- authentication
- direct-answer

### Answer objective
Help the user install the complete xHR Assistant plugin for the correct host and operating system, then start the first authenticated session safely. Keep this separate from installing an X-HR product app from the [App Store]({{app_store_url}}).

### Instructions
- Answer directly without calling executable tools or attempting to install the plugin on the user's machine.
- First identify the host (Codex, Claude Code, or Google Antigravity/agy CLI) and operating system. If the user has not said, ask one short clarification question before giving a command.
- Tell the user to install only the payload matching the machine. The current marketplace mapping is Windows x64: `xhr-assistant`; macOS Apple Silicon: `xhr-assistant-macos`; Linux x64: `xhr-assistant-linux-x64`; Linux arm64: `xhr-assistant-linux-arm64`. Do not invent a macOS Intel payload.
- Treat the public repository URL below as the source for the internal marketplace installation commands: `https://github.com/xhr-labs/agent-xhr-plugins`.
- Do not tell users to register the bundled MCP server separately with `codex mcp add` or `claude mcp add`. The plugin installation includes the skills, MCP configuration, native launcher, and runtime.
- Never ask the user to paste an access token into chat or a tool argument. Authentication must use the private xHR sign-in window or the locally returned `auth token` command.
- Do not claim installation, authentication, or a restart succeeded unless the user confirms it.
- If the user means an X-HR product app rather than the desktop/CLI plugin, route them to the [App Store]({{app_store_url}}) guidance instead.

### Supported installation flows

#### Codex

Register the marketplace once, then install the plugin name matching the operating system:

```bash
codex plugin marketplace add https://github.com/xhr-labs/agent-xhr-plugins
codex plugin add <plugin>@xhr
```

Use `xhr-assistant` on Windows, `xhr-assistant-macos` on macOS Apple Silicon, `xhr-assistant-linux-x64` on Linux x64, or `xhr-assistant-linux-arm64` on Linux arm64.

#### Claude Code

Register the marketplace once, then install the matching plugin:

```bash
claude plugin marketplace add https://github.com/xhr-labs/agent-xhr-plugins
claude plugin install <plugin>@xhr
```

#### Google Antigravity or agy CLI

Antigravity does not use a plugin marketplace. Clone the repository and run the bundled installer from the matching payload:

```bash
git clone --depth 1 https://github.com/xhr-labs/agent-xhr-plugins xhr-marketplace
./xhr-marketplace/plugins/xhr-assistant-macos/bin/xhr-assistant install antigravity
```

Use `plugins/xhr-assistant/bin/xhr-assistant.exe` on Windows, `plugins/xhr-assistant-macos` on macOS Apple Silicon, and the appropriate Linux directory on Linux. Re-running the installer refreshes the Antigravity registration after the package moves or changes.

### After installation

1. Close the current agent task or session and start a new one so the host loads the plugin skills and MCP tools.
2. Ask an xHR question such as "Show my leave balance." The first request that needs a protected operation may request authentication.
3. Generate an access token in X-HR, then use the private sign-in prompt or the exact local `auth token` command returned by the plugin.
4. Retry the original request.

The first protected request may also download the plugin's Python runtime once. The machine needs network access for that bootstrap. Users do not need to install Python or a virtual environment for a released plugin.

### Common installation failures

- **MCP startup failed or file not found**: the selected payload does not match the operating system. Remove it and install the matching payload.
- **The skills or tools are missing**: restart the host and start a new task or session.
- **The first request mentions the Python runtime**: allow the one-time runtime download and retry. If it still fails, the installed binary's `setup` health command can be used by the user.
- **No sign-in window appears**: use the exact local authentication command returned by the plugin. Never request the token in chat.
- **The token is rejected**: generate a fresh token in the same xHR environment that the plugin is using.
- **macOS refuses to run the binary**: follow the organization's approved code-signing or quarantine-removal procedure, then retry. Do not download an unrelated binary.

### Scope boundary

This leaf explains installation and first-use sign-in. For updating, uninstalling, switching environments, checking authentication, running `setup` or `doctor`, and recovering from stale plugin caches, use `agent_cli_plugin_management_help`.
