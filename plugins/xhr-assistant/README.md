# xHR Assistant

`xhr-assistant` is an agent plugin for Codex, Claude Code, and Google
Antigravity that exposes a small set of native xHR domain skills while
keeping the detailed skill tree and execution runtime under central control.
Codex and Claude Code install it as a marketplace plugin; Antigravity is
registered by the bundled `xhr-assistant install antigravity` command.

The plugin deliberately exposes only three MCP tools:

- `read` reads an approved `skills/**/SKILL.md` entrypoint from the runtime.
- `exec` executes only scripts declared by an approved leaf skill.
- `authenticate` opens the private xHR token dialog; the token never passes
  through the model.

The contracts mirror the existing `agent-service` runtime so the same
`agent-scripts` skill tree can be used by Codex, Claude Code, and other
compatible agents. The plugin ships one shared skill set, runtime, and MCP
binary; only the thin host manifests differ (`.codex-plugin/` for Codex,
`.claude-plugin/` for Claude Code).

## Architecture

```text
User request
  -> native domain skill (skills/xhr-*/SKILL.md)
  -> MCP read(index SKILL.md)
  -> MCP read(leaf SKILL.md)
  -> MCP exec(exact leaf-declared script)
  -> xHR API
```

```text
xhr-assistant/
|-- .codex-plugin/
|   |-- plugin.json               # Codex manifest
|   `-- mcp.json                  # Codex MCP launcher (Codex plugin cache)
|-- .claude-plugin/
|   |-- plugin.json               # Claude Code manifest
|   `-- mcp.json                  # Claude MCP launcher (${CLAUDE_PLUGIN_ROOT})
|-- skills/                       # Native host-discovered domain routers
|   |-- xhr-timeoff/SKILL.md      # One router per user-facing runtime domain
|   |-- xhr-attendance/SKILL.md   # (21 domains: employee, payroll, workbench,
|   |-- ...                       #  documents, calendar, workflow, helpdesk, ...)
|   `-- xhr-general/SKILL.md      # Catch-all router into the root skill index
|-- runtime/
|   |-- agent-scripts/            # Vendored skill-tree snapshot
|   `-- python/                   # Vendored CPython for exec (not in Git)
`-- docs/
    |-- architecture.md
    |-- authentication.md
    |-- tool-contracts.md
    `-- runtime-dependency.md
```

## Repository status

This repository contains the plugin manifest, domain routing skills, a local
stdio MCP server, auth CLI, restricted `read`/`exec`/`authenticate` tools, and design
contracts. The `agent-scripts` runtime is vendored into the plugin. Users
generate access tokens in xHR Platform and add them to the local credential
store through the bundled CLI.

## Local development

For complete plugin installation through a local, internal Git, or public
marketplace on either host, see [docs/installation.md](docs/installation.md).
Do not install the bundled MCP separately with `codex mcp add` or
`claude mcp add`.

Create an environment and install the package:

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
```

When running from an editable development install, initialize and inspect the
user config with:

```bash
xhr-assistant auth status
```

Generate an access token in xHR Platform, then add it through the hidden prompt:

```bash
xhr-assistant auth token
```

For a plugin installation on Windows, the bundled executable is intentionally
not added to `PATH`. Locate the newest installed copy and invoke it with:

```powershell
# Codex installation
$xhrAssistant = Get-ChildItem "$env:USERPROFILE\.codex\plugins\cache\*\xhr-assistant\*\bin\xhr-assistant.exe" -File |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
& $xhrAssistant.FullName auth token
```

```powershell
# Claude Code installation
$xhrAssistant = Get-ChildItem "$env:USERPROFILE\.claude\plugins\cache\*\xhr-assistant*\bin\xhr-assistant.exe" -File -Recurse |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
& $xhrAssistant.FullName auth token
```

Both hosts share the same OS credential store entry, so authenticating once
covers Codex and Claude Code installations on the same machine.

The `AUTHENTICATION_REQUIRED` result returned by the MCP `exec` tool includes
the exact absolute command for its running installed binary, which is the
preferred command to show to an end user.

The plugin targets production by default; `xhr-assistant config set-env
sandbox|dev|prod` (or `config set-url <url>`) retargets the machine-wide
configuration — see
[docs/installation.md](docs/installation.md#environment-selection-optional).

For non-interactive setup, pass the token through standard input rather than a
command-line argument:

```bash
printf '%s' "$XHR_AUTHORIZATION" | xhr-assistant auth token --stdin
```

The CLI validates the token and stores it in the OS credential store. The MCP calls
`{XHR_API_BASE_URL}/v1/im/me` with that bearer token before every `exec`, derives
company, employee, and group context from its `data` object, and writes only
non-secret account metadata to `config.json`.

Start the MCP server directly on Windows with:

```bash
bin/xhr-assistant.exe mcp
```

Linux and macOS release artifacts contain `bin/xhr-assistant` instead. Each
artifact carries two platform-specific launchers: `.codex-plugin/mcp.json`
locates the newest installed binary in the Codex plugin cache, and
`.claude-plugin/mcp.json` launches the binary through `${CLAUDE_PLUGIN_ROOT}`.
Installed users do not need Python, a virtual environment, or packages on
`PATH`.

Build or refresh the executable for the current platform with:

```bash
python scripts/build_executable.py
```

Build the vendored Python runtime that `exec` uses to run leaf scripts:

```bash
python scripts/build_python_runtime.py
```

Package it with a matching target such as `windows-x64`, `linux-x64`,
`linux-arm64`, or `macos-arm64`:

```bash
python scripts/package_release.py --target linux-x64
```

PyInstaller binaries must be built on their target operating system. The
GitHub Actions release workflow builds and tests all four targets, uploads one
plugin artifact per target, and attaches them to tagged GitHub releases.
The checked-in `.codex-plugin/mcp.json` and `.claude-plugin/mcp.json` are the
Windows development launchers; generated Linux and macOS archives replace them
with their native executable path. `bin/` and `runtime/python/` are built
locally (or in CI) and are not committed.

`XHR_AGENT_SCRIPTS_ROOT` is available only as an explicit development/test
override. Installed plugins use `runtime/agent-scripts`.

## Development and deploy workflow

`runtime/agent-scripts` is a committed, reviewed snapshot; `bin/` and
`runtime/python/` are build outputs and stay untracked. Every published change
follows one of two flows.

### Flow 1: plugin code changes (src/, skills/, scripts/, docs)

1. Edit and test: `python -m pytest -q`.
2. Rebuild the binary when MCP server code changed:
   `python scripts/build_executable.py`.
3. Bump the version with `python scripts/bump_version.py --patch` (or
   `--minor`, or an explicit `0.x.y`). It rewrites `pyproject.toml`,
   `.claude-plugin/plugin.json`, and `.codex-plugin/plugin.json` (base plus
   fresh `+codex.<timestamp>` build metadata) together;
   `scripts/check_versions.py` guards the alignment in CI and
   `scripts/package_release.py` refuses to package when they diverge.
4. Commit and push.

### Flow 2: runtime updates pulled from agent-scripts

1. Land and test the change in the `agent-scripts` repository first.
2. Pull a fresh snapshot:
   `python scripts/sync_agent_scripts.py ../agent-scripts`.
3. Review the vendored diff and
   `runtime/agent-scripts/runtime-version.json`; do not publish a snapshot
   whose provenance reports `dirty: true` or an unreviewed branch.
4. If new scripts import new third-party packages, add them to
   `runtime-requirements.txt` and rebuild with
   `python scripts/build_python_runtime.py --force`.
5. If a new user-facing domain appeared, add a `skills/xhr-<domain>/SKILL.md`
   router following the existing nine-step pattern with a capability-accurate
   description; `xhr-general` covers domains without a dedicated router.
6. Run tests, bump the version, commit, and push.

### Verifying locally against real hosts

The development junction in `xhr-plugins` points at this working tree.

- Codex installs from the junction: refresh the build metadata with
  `python scripts/bump_version.py --stamp` (a fresh cache directory sidesteps
  locked or read-only cache entries) and run
  `codex plugin add xhr-assistant@xhr`.
- Claude Code installs from a marketplace snapshot and caches by version, so
  a plain reinstall serves stale files. Bump the version, then:
  `claude plugin marketplace update xhr`, `claude plugin uninstall
  xhr-assistant@xhr`, `claude plugin install xhr-assistant@xhr`.
- Restart the host or open a new session; skills and MCP tools only enter new
  sessions.

### Releasing

Tag `v*` (matching the manifest base version) and push the tag. GitHub
Actions then runs two publishing stages:

1. `publish` builds, tests, and packages all four platform targets (MCP
   executable plus vendored Python runtime) and attaches the archives to the
   GitHub release — the permanent per-version archive.
2. `publish-marketplace` materializes each platform package onto its own
   orphan branch of `xhr-labs/agent-xhr-plugins` (`release/windows-x64`,
   `release/linux-x64`, `release/linux-arm64`, `release/macos-arm64`).
   Every branch holds exactly one commit with the
   marketplace catalogs plus the plugin payload, so the marketplace never
   accumulates artifact history. This stage needs the `CI_PIPELINE_PAT`
   secret with write access to `agent-xhr-plugins`.

End users then install the branch matching their platform:

```bash
codex plugin marketplace add xhr-labs/agent-xhr-plugins --ref release/windows-x64
codex plugin add xhr-assistant@xhr
```

See [docs/installation.md](docs/installation.md) for the Claude Code
equivalent and the full installation matrix.

## Runtime dependency

The plugin vendors an approved `agent-scripts` snapshot so installed copies do
not need Git access. Refresh it with
`python scripts/sync_agent_scripts.py ../agent-scripts` and review the generated
provenance described in [docs/runtime-dependency.md](docs/runtime-dependency.md).

It also vendors a relocatable CPython runtime at `runtime/python` (built by
`scripts/build_python_runtime.py`, excluded from Git) that `exec` uses to run
leaf scripts with the dependencies declared in `runtime-requirements.txt`.

## Design principles

- Native skills perform coarse domain routing only.
- Detailed skill selection happens by reading the runtime skill tree.
- A leaf `SKILL.md` must be read before execution.
- `read` renders allowlisted `{{placeholder}}` values from the vendored
  `skill-template-params.json` before returning content.
- Script paths and arguments must never be guessed.
- `exec` is restricted execution, not a general-purpose remote shell.
- xHR credentials stay in the managed MCP runtime, not in the agent host.

## Authentication context

The model never supplies `Authorization`, `Xhr-Employee-Id`, or
`Xhr-Company-Id` as `exec` arguments. The MCP connection authenticates the
caller, the server derives a trusted request context, and `exec` injects that
context into the `agent-scripts` process as `REQUEST_HEADERS`. See
[docs/authentication.md](docs/authentication.md).

For local MCP usage, account tokens persist in the operating system credential
store so users do not sign in before every `exec` call. The normal configuration
file contains no bearer token. OAuth is outside the current local-plugin scope.
