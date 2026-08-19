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

Each platform package includes a native self-contained executable containing
the MCP server and auth CLI dependencies: `bin/xhr-assistant.exe` on Windows
and `bin/xhr-assistant` on Linux/macOS. It also includes a relocatable CPython
distribution at `runtime/python` that `exec` uses to run leaf scripts — the
frozen MCP binary is not a script interpreter, and script dependencies
(`runtime-requirements.txt`) are preinstalled there. Each host launches that binary through
its own generated launcher so installed users do not need Python:

- `.codex-plugin/mcp.json` locates the newest installed binary in the Codex
  plugin cache;
- `.claude-plugin/mcp.json` launches `${CLAUDE_PLUGIN_ROOT}/bin/xhr-assistant`
  from the Claude Code plugin installation.

There is intentionally no `.mcp.json` at the plugin root: Claude Code
auto-loads that path, so a shared root launcher could not stay host-specific.

Native artifacts are released separately for Windows x64, Linux x64/arm64,
and macOS arm64 (Apple Silicon; GitHub is retiring Intel macOS runners and
the fleet is Apple Silicon). A PyInstaller binary is always built on its
target OS; it
is not copied between operating systems.

## Physical and public paths

The physical runtime is mounted at `runtime/agent-scripts`, while public tool
paths remain compatible with `agent-service`:

```text
public:   skills/timeoff/submit_my_leave_request/SKILL.md
physical: runtime/agent-scripts/skills/timeoff/submit_my_leave_request/SKILL.md
```

This prevents runtime leaf skills from being discovered as top-level plugin
skills while preserving existing leaf instructions.
