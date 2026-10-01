---
name: helpdesk-agent-cli-plugin-management-help
description: Explain how to update, remove, authenticate, configure, inspect, and troubleshoot the xHR Assistant plugin for Codex, Claude Code, and Google Antigravity. Use for Agent CLI plugin management questions, not in-product App Store app management.
---

# Agent CLI Plugin Management Help

## Intent: helpdesk-agent-cli-plugin-management-help
### User request patterns
- update the xHR Assistant plugin
- uninstall the xHR Assistant plugin
- temporarily disable the xHR plugin
- check whether the plugin is installed
- check whether xHR Assistant is authenticated
- sign out of xHR Assistant
- switch the xHR Assistant environment
- use the sandbox or dev environment with the plugin
- diagnose missing skills or tools after an update
- check the plugin runtime health
- run the xHR Assistant doctor check
- fix a stale plugin cache

### Retrieval tags
- helpdesk
- agent-cli
- xhr-assistant
- plugin
- manage
- update
- uninstall
- authentication
- environment
- setup
- doctor
- troubleshooting
- direct-answer

### Answer objective
Help users safely maintain an installed xHR Assistant plugin: verify host state, update or remove the correct OS payload, manage local authentication and environment selection, and diagnose runtime or session problems. Keep this separate from managing installed X-HR product apps in the [App Store]({{app_store_url}}).

### Instructions
- Answer directly without calling executable tools or changing the user's machine.
- Identify the host and operating system before giving a host-specific command. Preserve the installed payload name; do not substitute a Windows, macOS, or Linux plugin.
- Never ask for or accept an access token in chat. Tokens remain in the operating system credential store and should be entered only through the private prompt or local command.
- Do not tell users to add a second manual MCP server entry. The plugin owns its MCP registration.
- Treat commands that remove plugins, sign out, switch environments, or remove stale files as user-controlled changes. Explain the effect and ask the user to run or confirm them; do not claim they already ran.
- `setup` checks runtime health and may bootstrap the runtime. `doctor` is read-only and reports issues plus cleanup commands; do not recommend destructive cleanup blindly.
- If the user means managing an X-HR product app, route them to the [App Store]({{app_store_url}}) guidance instead.

### Check installed state

For Codex:

```bash
codex plugin marketplace list
codex plugin list
```

For Claude Code:

```bash
claude plugin marketplace list
claude plugin list
```

For Antigravity, the plugin is registered globally by the bundled installer. The user can rerun the matching `install antigravity` command to refresh the registration after an update.

### Update

For Codex, refresh the marketplace and run `plugin add` again with the installed OS-specific plugin name. Codex does not use a separate plugin upgrade command:

```bash
codex plugin marketplace upgrade xhr
codex plugin add <plugin>@xhr
```

For Claude Code:

```bash
claude plugin marketplace update xhr
claude plugin update <plugin>@xhr
```

For Antigravity, pull the marketplace clone and rerun the matching installer:

```bash
git -C xhr-marketplace pull
./xhr-marketplace/plugins/xhr-assistant-macos/bin/xhr-assistant install antigravity
```

After any update, close running agent sessions and start new ones. The host can remove old version files while an old session still has the previous server process open.

### Remove or temporarily disable

For Codex:

```bash
codex plugin remove <plugin>@xhr
```

For Claude Code:

```bash
claude plugin uninstall <plugin>@xhr
```

For Antigravity, run the matching bundled command:

```bash
./xhr-marketplace/plugins/xhr-assistant-macos/bin/xhr-assistant uninstall antigravity
```

Remove the `xhr` marketplace only when no other installed plugin uses it. Removing the plugin registration does not automatically delete the shared xHR credential. If the user also wants to sign out, use the installed binary's `auth logout` command.

### Authentication and environment

Use the installed binary's local commands when the host returns its path:

```bash
xhr-assistant auth status
xhr-assistant auth logout
xhr-assistant config show
```

If the binary is not on `PATH`, use the exact absolute command returned by the authentication-required response or the copy inside the host's plugin cache. Do not guess a cache version or path.

The plugin targets production by default. Supported named environments are `prod`, `sandbox`, and `dev`:

```bash
xhr-assistant config set-env sandbox
xhr-assistant config set-env dev
xhr-assistant config set-env prod
xhr-assistant config show
```

The CLI also supports `config set-url <url>` for a custom API address and `config set-app-url <url>` for a custom frontend address. Only recommend custom addresses when the user's organization provides one.

Switching environments clears the cached identity and requires a new token generated in the selected environment. Restart the agent session after changing the environment, then authenticate again. Environment selection is machine-wide for the default config, so it can affect multiple host installations on that machine.

### Runtime health and troubleshooting

Run the commands from the installed plugin cache or use the exact binary path returned by the plugin:

```bash
<plugin-cache>/bin/xhr-assistant setup
<plugin-cache>/bin/xhr-assistant doctor
```

- **`setup` fails or the runtime is missing**: check network access for the one-time runtime bootstrap, then retry. Start a new session after a successful update or reinstall.
- **`doctor` reports a manual Codex MCP server entry**: remove the manually registered server only after reviewing the reported path, because it can shadow the plugin's managed server.
- **`doctor` reports an interpreter override**: unset development-only overrides such as `XHR_SCRIPT_PYTHON` or `XHR_AGENT_SCRIPTS_ROOT` unless the user deliberately needs them.
- **`doctor` reports a stale Windows-named cache on macOS or Linux**: install the correct per-OS plugin and follow the reported cleanup command only after confirming no old session is running.
- **Skills or tools disappeared after update**: close all old sessions and start a new one. Verify the host's plugin list before reinstalling.
- **Authentication is required again**: the token may have expired or the environment may have changed. Generate a token for the active environment and authenticate locally.
- **Requests use the wrong workspace or environment**: run `config show`, switch to the intended environment, restart the session, and authenticate again.
- **macOS or Linux shows a `.exe` error**: the Windows payload was installed; remove it and install the matching native payload.

### Scope boundary

This leaf covers plugin lifecycle and local runtime management. It does not manage X-HR employee data, product app installation, or raw MCP requests.
