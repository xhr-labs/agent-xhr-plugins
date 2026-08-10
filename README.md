# xHR Plugins Marketplace

This repository is the xHR plugin catalog for both Codex and Claude Code.
Plugin implementation, tests, native binaries, and release artifacts remain in
their own repositories.

Each host reads its own catalog file over the same `plugins/` payload:

- Codex: `.agents/plugins/marketplace.json`
- Claude Code: `.claude-plugin/marketplace.json`

## Local development layout

```text
xhr/
|-- xhr-assistant/                 # Plugin source repository
`-- xhr-plugins/                   # This marketplace repository
    |-- .agents/plugins/
    |   `-- marketplace.json       # Codex catalog
    |-- .claude-plugin/
    |   `-- marketplace.json       # Claude Code catalog
    `-- plugins/
        `-- xhr-assistant/         # Local junction to ../../xhr-assistant
```

The local junction is intentionally ignored by Git. It lets Codex and Claude
Code install the current development source without copying or extracting an
artifact.

## Local developer installation

Codex:

```powershell
codex plugin marketplace add C:\Users\TyLe\work\xhr\xhr-plugins
codex plugin add xhr-assistant@xhr
```

Claude Code:

```powershell
claude plugin marketplace add C:\Users\TyLe\work\xhr\xhr-plugins
claude plugin install xhr-assistant@xhr
```

Verify the installation:

```powershell
codex plugin marketplace list
codex plugin list
```

```powershell
claude plugin marketplace list
claude plugin list
```

Restart the host and open a new task after installation. On the first xHR
action, the bundled MCP returns the installed CLI command. Generate a token in
xHR Platform, run that command with `auth token`, then retry the action. The
token is stored once in the OS credential store and shared by both hosts.

To reset and test installation again:

```powershell
codex plugin remove xhr-assistant@xhr
codex plugin marketplace remove xhr
```

```powershell
claude plugin uninstall xhr-assistant@xhr
claude plugin marketplace remove xhr
```

Do not use `codex mcp add` or `claude mcp add`; the MCP server is installed
together with the plugin's skills and runtime.

## End-user installation

Pick the release branch matching your platform:

| Platform | Release branch |
|---|---|
| Windows x64 | `release/windows-x64` |
| Linux x64 | `release/linux-x64` |
| Linux arm64 | `release/linux-arm64` |
| macOS (Apple Silicon) | `release/macos-arm64` |

Add the marketplace at that branch, then install the plugin. Windows
examples — replace the branch name on other platforms:

```bash
# Codex
codex plugin marketplace add xhr-labs/agent-xhr-plugins --ref release/windows-x64
codex plugin add xhr-assistant@xhr
```

```bash
# Claude Code (no --ref flag; the branch goes in a #fragment)
claude plugin marketplace add xhr-labs/agent-xhr-plugins#release/windows-x64
claude plugin install xhr-assistant@xhr
```

```bash
# Antigravity / agy CLI on Windows (no marketplace support; the package registers itself)
git clone -b release/windows-x64 https://github.com/xhr-labs/agent-xhr-plugins xhr-marketplace
xhr-marketplace/plugins/xhr-assistant/bin/xhr-assistant.exe install antigravity
```

```bash
# Antigravity / agy CLI on macOS (Apple Silicon) and Linux
git clone -b release/macos-arm64 https://github.com/xhr-labs/agent-xhr-plugins xhr-marketplace
./xhr-marketplace/plugins/xhr-assistant/bin/xhr-assistant install antigravity
```

The binary is `bin\xhr-assistant.exe` on Windows and `bin/xhr-assistant` on
macOS/Linux — pick the release branch AND the binary name for your platform.

The Antigravity installer writes the MCP server entry into
`~/.gemini/config/mcp_config.json` (shared by the IDE, the agy CLI, and the
SDK) and copies the `xhr-*` skills into `~/.gemini/skills/`. Restart
Antigravity afterwards; re-run the same command after updating the clone,
and use `uninstall antigravity` to remove the registration. Requires plugin
release v0.1.9 or newer.

Restart the host or open a new session after installation. On the first xHR
action, the plugin returns the exact `auth token` command for its installed
binary: generate an access token in xHR Platform, run that command, paste the
token into the hidden prompt, and retry. The token lives in the OS credential
store and is shared by both hosts on the same machine.

Do not add the marketplace without a branch: the default branch carries only
the catalogs, so plugin installation fails with "Source path does not exist".
Release branches always hold the latest release; to update, run the host's
marketplace update command (`codex plugin marketplace upgrade xhr` /
`claude plugin marketplace update xhr`) and reinstall the plugin.

The local development folder is named `xhr-plugins`; the Git repository is
`xhr-labs/agent-xhr-plugins`.

## Public end-user installation

After xHR Assistant is published to a public plugin directory, users only open
**Plugins**, find **xHR Assistant**, and select **Install**. They do not clone
repositories, add a marketplace source, download an archive, or create a
junction.

## Release model

Local development uses the junction. On every `v*` tag of `xhr-assistant`,
its `publish-marketplace` release job force-pushes one orphan branch per
platform into this repository — `release/windows-x64`, `release/linux-x64`,
`release/linux-arm64`, `release/macos-arm64` — each holding a single
commit: the marketplace catalogs plus the materialized plugin package at
`plugins/xhr-assistant`.

Consequences:

- The default branch stays thin (catalogs and this README only).
- A release branch always weighs one artifact regardless of how many
  releases have shipped; superseded commits become unreachable and are
  garbage-collected by the Git host.
- End users add the marketplace at the branch matching their platform, for
  example `codex plugin marketplace add xhr-labs/agent-xhr-plugins --ref
  release/windows-x64`.
- The permanent per-version archive lives in the GitHub Releases of
  `xhr-assistant`, not in this repository.
