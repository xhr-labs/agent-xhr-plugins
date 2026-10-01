# Installation

`xhr-assistant` is installed as a complete plugin on Codex and on Claude Code.
Do not register its bundled MCP server separately with `codex mcp add` or
`claude mcp add`; the plugin manifest installs the domain skills, MCP
configuration, native executable, and vendored runtime as one unit.

One plugin package serves both hosts. Each host reads only its own manifest
directory:

- Codex reads `.codex-plugin/plugin.json`, which references
  `.codex-plugin/mcp.json`.
- Claude Code reads `.claude-plugin/plugin.json`, which references
  `.claude-plugin/mcp.json`.

## Local development installation

The recommended local layout uses two sibling repositories:

```text
xhr/
|-- xhr-assistant/                 # Plugin source
`-- xhr-plugins/                   # Marketplace catalog
    |-- .agents/plugins/marketplace.json      # Codex marketplace
    |-- .claude-plugin/marketplace.json       # Claude Code marketplace
    `-- plugins/
        `-- xhr-assistant/         # Junction to ../../xhr-assistant
```

On Windows, create the development junction once (adjust `C:\work\xhr` to
wherever the sibling repositories live):

```powershell
New-Item -ItemType Junction `
  -Path C:\work\xhr\xhr-plugins\plugins\xhr-assistant `
  -Target C:\work\xhr\xhr-assistant
```

### Codex

Register the non-default local marketplace and install the plugin:

```powershell
codex plugin marketplace add C:\work\xhr\xhr-plugins
codex plugin add xhr-assistant@xhr
```

Verify both states:

```powershell
codex plugin marketplace list
codex plugin list
```

Restart Codex and open a new task so the installed skills and MCP tools enter
the new task context.

To repeat a clean installation test:

```powershell
codex plugin remove xhr-assistant@xhr
codex plugin marketplace remove xhr
```

### Claude Code

Register the same marketplace directory and install the plugin:

```powershell
claude plugin marketplace add C:\work\xhr\xhr-plugins
claude plugin install xhr-assistant@xhr
```

Verify both states:

```powershell
claude plugin marketplace list
claude plugin list
```

Restart Claude Code or start a new session so the installed skills and MCP
tools enter the new context.

To repeat a clean installation test:

```powershell
claude plugin uninstall xhr-assistant@xhr
claude plugin marketplace remove xhr
```

The junction is a development convenience only. It is ignored by the
marketplace repository and must not be used as a production dependency.

## Internal end-user installation from Git

The Codex and Claude marketplaces have no per-platform awareness, so the
release automation publishes **one plugin directory per operating system** to
the `main` branch of `agent-xhr-plugins` (the same pattern npm uses for
per-platform packages such as `@esbuild/win32-x64`). Every directory is that
target's own release payload, verbatim — correct native launcher and correct
per-OS mcp.json. The Windows payload keeps the historical bare name so the
existing fleet updates without a reinstall:

```text
xhr-plugins/
|-- .agents/plugins/marketplace.json          # lists all four plugins
|-- .claude-plugin/marketplace.json           # lists all four plugins
`-- plugins/
    |-- xhr-assistant/                        # Windows x64
    |-- xhr-assistant-macos/                  # macOS (Apple Silicon)
    |-- xhr-assistant-linux-x64/
    `-- xhr-assistant-linux-arm64/
```

An internal user adds the marketplace once, then installs **the plugin that
matches their operating system**:

```bash
# Codex
codex plugin marketplace add https://github.com/xhr-labs/agent-xhr-plugins
codex plugin add xhr-assistant@xhr              # Windows
codex plugin add xhr-assistant-macos@xhr        # macOS (Apple Silicon)
codex plugin add xhr-assistant-linux-x64@xhr    # Linux x64
codex plugin add xhr-assistant-linux-arm64@xhr  # Linux arm64
```

```bash
# Claude Code
claude plugin marketplace add https://github.com/xhr-labs/agent-xhr-plugins
claude plugin install xhr-assistant@xhr              # Windows
claude plugin install xhr-assistant-macos@xhr        # macOS (Apple Silicon)
claude plugin install xhr-assistant-linux-x64@xhr    # Linux x64
claude plugin install xhr-assistant-linux-arm64@xhr  # Linux arm64
```

When upgrading, standard marketplace upgrade commands pull cleanly from
`main` (substitute the plugin name for your OS):

```bash
# Codex Upgrade — the codex CLI has no `plugin upgrade` subcommand;
# re-running `plugin add` installs the marketplace's newer version.
codex plugin marketplace upgrade xhr
codex plugin add xhr-assistant@xhr
```

```bash
# Claude Code Upgrade
claude plugin marketplace update xhr
claude plugin update xhr-assistant@xhr
```

After upgrading, **close running agent sessions and start new ones**: hosts
delete the old plugin version's files during the upgrade, and a session that
keeps its old server process running will fail with "plugin files were
removed" errors on its next tool call. When something looks off after an
upgrade, run the bundled health commands and share their output:

```bash
<plugin-cache>/bin/xhr-assistant setup    # runtime health (bootstraps if missing)
<plugin-cache>/bin/xhr-assistant doctor   # flags leftover config/caches with exact cleanup commands
```

### Antigravity (IDE and agy CLI)

Antigravity has no plugin marketplace, so the plugin package registers
itself. Clone the marketplace (`main` carries every platform payload) and run
the bundled installer from the directory that matches your operating system:

```powershell
# Windows
git clone --depth 1 https://github.com/xhr-labs/agent-xhr-plugins xhr-marketplace
xhr-marketplace\plugins\xhr-assistant\bin\xhr-assistant.exe install antigravity
```

```bash
# macOS (Apple Silicon) — the binary has no .exe suffix
git clone --depth 1 https://github.com/xhr-labs/agent-xhr-plugins xhr-marketplace
./xhr-marketplace/plugins/xhr-assistant-macos/bin/xhr-assistant install antigravity

# Linux: use plugins/xhr-assistant-linux-x64 or plugins/xhr-assistant-linux-arm64
```

The installer builds an Antigravity plugin bundle at
`~/.gemini/config/plugins/xhr-assistant/` — `plugin.json`, an
`mcp_config.json` pointing at the binary's absolute path, and the `xhr-*`
router skills — which the Antigravity IDE, the agy CLI, and the SDK all
ingest automatically from the global customization root. It also cleans up
locations used by installers before v0.1.14. Restart Antigravity; the
`read`/`exec`/`authenticate` tools and the domain skills load natively —
the agent must not spawn the binary itself or talk raw JSON-RPC to it.

Re-run the same command after moving or updating the package. Remove the
registration and skills with:

```powershell
xhr-marketplace\plugins\xhr-assistant\bin\xhr-assistant.exe uninstall antigravity
```

Token setup is unchanged — see
[Token setup after installation](#token-setup-after-installation).

## Public end-user installation

After publication to a public plugin directory, users do not add a marketplace
URL, download an archive, or extract files manually. They:

1. Open **Plugins** in a supported Codex or Claude Code surface.
2. Find **xHR Assistant**.
3. Select **Install**.
4. Start a new task or session.

The host downloads and installs the complete platform-compatible plugin
package.

## Token setup after installation

Authentication is on first use. The `read` tool works without an xHR token.
The first workflow that calls `exec` returns the installed CLI command when no
credential exists. The user:

1. Generates an access token in xHR Platform.
2. Runs the returned command ending in `auth token`.
3. Pastes the token into the hidden prompt.
4. Retries the original request.

The CLI validates the token through `/v1/im/me` and stores it in the operating
system credential store. It never writes the token to plugin files or
`config.json`. The credential store entry is shared, so authenticating once
covers every host installation on the same machine.

## Environment selection (optional)

Installations target production (`https://api.x-hr.co`) by default. To point
the plugin at another environment, run the bundled CLI once after
installation — the setting lives in the per-machine `config.json` and applies
to every host on that machine:

```bash
xhr-assistant config set-env sandbox     # API: https://api.sandbox.x-hr.co, App: https://sandbox.x-hr.co
xhr-assistant config set-env dev         # API: https://api.dev.x-hr.ai, App: https://dev.x-hr.ai
xhr-assistant config set-env prod        # back to production (API: https://api.x-hr.co, App: https://app.x-hr.co)
xhr-assistant config set-url <url>       # custom HTTP(S) API base URL
xhr-assistant config set-app-url <url>   # custom HTTP(S) frontend App URL
xhr-assistant config show                # print active environment and URLs
```

Switching environments clears the cached identity and requires a new
`authenticate`/`auth token` with a token generated on that environment.
Restart the agent session afterwards so the MCP server reloads the
configuration. Tokens are environment-specific; the host CLIs cannot pass an
environment at install time, which is why this is a post-install command.

To run two environments side by side, register a second MCP server entry
whose `env` sets `XHR_ASSISTANT_CONFIG_FILE` to a separate config file (and
`XHR_API_BASE_URL` for its first run).
