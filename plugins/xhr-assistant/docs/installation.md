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

Before sharing the marketplace, release automation must materialize a complete,
platform-specific plugin at `plugins/xhr-assistant`. It must not publish the
local junction. The resulting Git marketplace must contain:

```text
xhr-plugins/
|-- .agents/plugins/marketplace.json
|-- .claude-plugin/marketplace.json
`-- plugins/
    `-- xhr-assistant/
        |-- .codex-plugin/
        |   |-- plugin.json
        |   `-- mcp.json
        |-- .claude-plugin/
        |   |-- plugin.json
        |   `-- mcp.json
        |-- bin/
        |-- skills/
        `-- runtime/
```

The `publish-marketplace` job in the release workflow materializes each
platform package onto its own orphan branch of `agent-xhr-plugins`
(`release/windows-x64`, `release/linux-x64`, `release/linux-arm64`,
`release/macos-arm64`). Each branch always contains
exactly one commit with the latest release, so the marketplace repository
never accumulates artifact history.

An internal user installs the marketplace branch matching their platform:

```bash
# Codex (Windows example)
codex plugin marketplace add xhr-labs/agent-xhr-plugins --ref release/windows-x64
codex plugin add xhr-assistant@xhr
```

```bash
# Claude Code (Windows example; no --ref flag, the branch goes in a #fragment)
claude plugin marketplace add xhr-labs/agent-xhr-plugins#release/windows-x64
claude plugin install xhr-assistant@xhr
```

Both command sets are verified against released versions (v0.1.8 and later).
The marketplace may also be added from a full HTTPS Git URL, which guarantees
anonymous access on machines with custom SSH configurations. Do not add the
marketplace without a branch: the default branch carries only the catalogs,
so installation fails with "Source path does not exist". The local
development folder is named `xhr-plugins`, while the Git repository is
`xhr-labs/agent-xhr-plugins`.

### Antigravity (IDE and agy CLI)

Antigravity has no plugin marketplace, so the plugin package registers
itself. Get the platform package onto disk (clone the matching release
branch or extract the GitHub release archive), then run the bundled
installer once:

```powershell
# Windows
git clone -b release/windows-x64 https://github.com/xhr-labs/agent-xhr-plugins xhr-marketplace
xhr-marketplace\plugins\xhr-assistant\bin\xhr-assistant.exe install antigravity
```

```bash
# macOS (Apple Silicon) / Linux — the binary has no .exe suffix
git clone -b release/macos-arm64 https://github.com/xhr-labs/agent-xhr-plugins xhr-marketplace
./xhr-marketplace/plugins/xhr-assistant/bin/xhr-assistant install antigravity
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
xhr-assistant config set-env sandbox     # https://api.sandbox.x-hr.co
xhr-assistant config set-env dev         # https://api.dev.x-hr.ai
xhr-assistant config set-env prod        # back to production
xhr-assistant config set-url <url>      # any other HTTP(S) base URL
xhr-assistant config show               # print the active environment
```

Switching environments clears the cached identity and requires a new
`authenticate`/`auth token` with a token generated on that environment.
Restart the agent session afterwards so the MCP server reloads the
configuration. Tokens are environment-specific; the host CLIs cannot pass an
environment at install time, which is why this is a post-install command.

To run two environments side by side, register a second MCP server entry
whose `env` sets `XHR_ASSISTANT_CONFIG_FILE` to a separate config file (and
`XHR_API_BASE_URL` for its first run).
