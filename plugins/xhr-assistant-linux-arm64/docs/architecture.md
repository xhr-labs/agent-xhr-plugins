# Architecture

## Why domain router skills

Codex, Claude Code, and other skill-aware hosts already place native skill
metadata in model context. Publishing every xHR leaf as a native skill would make that initial
catalog unnecessarily large. This plugin publishes one skill per major domain
and keeps the full tree in `agent-scripts`.

## Request lifecycle

1. The host selects a native `xhr-*` domain skill.
2. The domain skill calls `read` for the matching domain index.
3. The model follows only child entrypoints returned by that index.
4. The model calls `read` for the selected leaf `SKILL.md`.
5. The model collects and validates the leaf's required arguments.
6. The model calls `exec` using the exact contract declared by the leaf.
7. The MCP runtime validates the target, authorization, side-effect policy,
   and arguments before dispatching to `agent-scripts`.

Before dispatch, the runtime constructs `REQUEST_HEADERS` from the authenticated
MCP session. This mirrors `agent-service` without exposing identity headers or
tokens to the model.

Local and remote transports use the same execution context but different token
ownership:

- local stdio MCP loads and refreshes credentials through the operating system
  credential store;
- remote HTTP MCP verifies the bearer token supplied by the authenticated MCP
  host on every request.

## Trust boundaries

The host model and skill instructions are orchestration inputs, not security
boundaries. Enforcement belongs to the MCP runtime:

- `read` is confined to approved runtime-relative skill entrypoints.
- `exec` is confined to declared scripts beneath approved leaf directories.
- command mode accepts only the restricted grammar supported by
  `agent-service`.
- structured mode accepts a runtime-relative path and native argument object.
- credentials are injected server-side.
- employee and company scope are derived from trusted authentication context,
  not from `exec` arguments;
- authorization is checked for every request.
- writes are audited and follow the runtime's confirmation policy.

Each platform package includes a thin native launcher (`bin/xhr-assistant.exe`
on Windows, `bin/xhr-assistant` on Linux/macOS — a small static Rust binary,
see `launcher/`) and one relocatable CPython distribution at `runtime/python`.
That single interpreter runs everything: the MCP server and auth CLI
(`python -m xhr_assistant_mcp`, with the package and its dependencies
preinstalled in the runtime's site-packages) and the agent-scripts leaf
scripts spawned by `exec`. The launcher ensures the runtime exists
(downloading the version-pinned archive when a marketplace install ships
without it), scrubs environment variables that would point the interpreter at
a foreign stdlib (`PYTHONHOME` and friends), and hands off. Each host
launches it through its own generated configuration so installed users do not
need Python:

- `.codex-plugin/mcp.json` locates this release's own binary in the Codex
  plugin cache: the cache keeps one directory per installed version, and the
  launcher command is generated at package time with that exact version
  embedded, so a cache holding several versions always launches the binary
  that shipped with the manifest;
- `.claude-plugin/mcp.json` launches `${CLAUDE_PLUGIN_ROOT}/bin/xhr-assistant`
  from the Claude Code plugin installation.

There is intentionally no `.mcp.json` at the plugin root: Claude Code
auto-loads that path, so a shared root launcher could not stay host-specific.

Native artifacts are released separately for Windows x64, Linux x64/arm64,
and macOS arm64 (Apple Silicon; GitHub is retiring Intel macOS runners and
the fleet is Apple Silicon). Each release leg builds its own launcher and
runtime on its target OS: the runtime installs binary wheels that must match
the platform, and the launcher simply builds natively alongside it.

Because neither the Codex nor the Claude marketplace is platform-aware, the
marketplace publishes one plugin per target (`xhr-assistant` for Windows —
the historical name, kept so the existing fleet updates in place —
`xhr-assistant-macos`, `xhr-assistant-linux-x64`, `xhr-assistant-linux-arm64`),
each taken verbatim from its own release archive so every install gets the
launcher and mcp.json built for its OS. `scripts/stage_marketplace.py` owns
that layout and rewrites both marketplace manifests, and refuses to publish a
payload whose launcher does not match its platform.

## Physical and public paths

The physical runtime is mounted at `runtime/agent-scripts`, while public tool
paths remain compatible with `agent-service`:

```text
public:   skills/timeoff/submit_my_leave_request/SKILL.md
physical: runtime/agent-scripts/skills/timeoff/submit_my_leave_request/SKILL.md
```

This prevents runtime leaf skills from being discovered as top-level plugin
skills while preserving existing leaf instructions.
