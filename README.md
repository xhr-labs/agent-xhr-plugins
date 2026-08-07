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

## Internal end-user installation

Once this repository is published and `plugins/xhr-assistant` contains a real
platform-specific release package, an internal user installs it from Git:

```bash
# Codex
codex plugin marketplace add xhr-labs/agent-xhr-plugins --ref <release-ref>
codex plugin add xhr-assistant@xhr
```

```bash
# Claude Code
claude plugin marketplace add xhr-labs/agent-xhr-plugins
claude plugin install xhr-assistant@xhr
```

The user may alternatively install `xhr-assistant` from marketplace `xhr`
through `/plugins` in Codex CLI, the Plugins Directory in the Codex desktop
app, or the `/plugin` command in Claude Code.

`<release-ref>` must be replaced with the immutable release branch or tag
before these commands are published to end users. The local development
folder is named `xhr-plugins`; the Git repository is
`xhr-labs/agent-xhr-plugins`.

## Public end-user installation

After xHR Assistant is published to a public plugin directory, users only open
**Plugins**, find **xHR Assistant**, and select **Install**. They do not clone
repositories, add a marketplace source, download an archive, or create a
junction.

## Release model

Local development uses the junction. Production release automation should
replace it in a staging checkout with the platform-specific, versioned
`xhr-assistant` artifact before publishing the marketplace.
