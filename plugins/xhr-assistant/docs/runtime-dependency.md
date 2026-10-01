# Vendored runtime strategy

## Decision

`xhr-assistant` ships two vendored runtimes:

- `runtime/agent-scripts`: a snapshot of the `agent-scripts` skill tree. The
  installed plugin does not require a Git submodule, a sibling repository, or
  a runtime clone.
- `runtime/python`: the single relocatable CPython distribution
  (python-build-standalone) that runs everything on installed machines: the
  MCP server itself (`python -m xhr_assistant_mcp`, started by the native
  launcher in `bin/`) and the leaf scripts spawned by `exec`. It carries the
  packages from `runtime-requirements.txt` and tkinter (for the
  authentication dialog), because installed machines cannot be assumed to
  have Python.
- `lib/xhr_assistant_mcp`: the MCP server package itself, shipped in the
  payload rather than installed into the runtime (the launcher puts `lib/`
  on `PYTHONPATH`). This is what keeps the runtime identical across plugin
  releases: server changes travel with the lightweight git payload, and an
  upgrade never re-downloads the interpreter.

This makes the package self-contained: MCP `read` can navigate the skill tree
and MCP `exec` can run declared scripts on any installed machine.

## Python runtime

Build or rebuild the interpreter for the current platform with:

```bash
python scripts/build_python_runtime.py
```

`runtime/python` is not committed to Git; every developer machine and CI
release target builds its own copy. `runtime-requirements.txt` declares the
third-party packages that `agent-scripts` imports (`httpx`,
`pydantic-settings`) and must stay in sync with the vendored snapshot when
`agent-scripts` gains new dependencies. The build prunes pip, setuptools,
tests, headers, and bytecode caches from the distribution — installed
machines only run scripts, they never install packages.

Bootstrap belongs to the native launcher (`launcher/`, shipped as
`bin/xhr-assistant[.exe]`). When a marketplace install ships without a
bundled runtime, the launcher detects the host OS/architecture and downloads
the runtime archive before starting the server. The download is pinned to
the release that matches the installed plugin version
(`releases/download/v<base>/...`) so an old install never picks up a newer,
untested runtime; the `latest` release is only a fallback when the pinned
asset is unavailable. Every failed step is logged to stderr so a broken
bootstrap is diagnosable from the MCP server log. `xhr-assistant setup` is a
health check: it runs the runtime import probe and reports the interpreter
status, and `xhr-assistant doctor` reports environment leftovers (manual
server entries, stale caches, override variables, old store entries) with
the exact cleanup commands.

Cold starts are invisible to the host: MCP hosts kill servers that do not
answer `initialize` within a short startup window (codex defaults to 10s),
which no download can beat. When the store is cold, the launcher acts as a
**warm-start proxy** — it answers the MCP handshake itself in milliseconds,
downloads the runtime in the background (a cross-launcher lock collapses
concurrent sessions into one download), holds incoming requests, then starts
the real server, replays the handshake, and pipes transparently. The first
tool call on a fresh machine simply takes the download time; nothing else
ever notices. If the download fails, every request receives a clear JSON-RPC
error naming the cause instead of a dead server.

Downloaded runtimes live in a per-machine **runtime store**, outside any
host's plugin cache, keyed by **runtime identity**: `runtime/runtime-id.txt`
is a hash of the CPython build plus `runtime-requirements.txt`, written at
build time, so every release asking for the same runtime shares one store
entry (`py-<id>-<target>`) and upgrading downloads nothing. Only editing
`runtime-requirements.txt` or the CPython version triggers a new download,
once per machine. The store lives under the platform data directory
(`XHR_RUNTIME_STORE_DIR` overrides). Hosts delete a
plugin version's cache directory when upgrading; a runtime inside it would
strand every running session of the old version mid-flight. The store
survives host cache lifecycles, is shared by every host on the machine, and
makes upgrades cheap: an unchanged runtime version is never downloaded
again. A runtime bundled inside the payload (self-contained archives,
development trees) still takes precedence over the store.

The launcher also scrubs the environment before any Python process exists:
`PYTHONHOME`, `PYTHONPATH`, and related variables exported by outer tool
chains (uv trampolines, conda) would point the vendored interpreter at a
foreign stdlib or site-packages.

For development and tests, `XHR_SCRIPT_PYTHON` overrides the interpreter used
by `exec`; a source checkout defaults to the current interpreter.

## Synchronizing

From the plugin repository:

```bash
python scripts/sync_agent_scripts.py ../agent-scripts
```

The sync copies `skills/`, `src/`, and required template/documentation files.
It excludes Git metadata, virtual environments, caches, bytecode, tests, and
other development artifacts.

The generated `runtime/agent-scripts/runtime-version.json` records repository,
commit, branch, dirty state, timestamp, and sync mode. Do not publish a snapshot
whose provenance reports `dirty: true` without explicitly reviewing why.

Provenance exists for maintainers only: release packaging deliberately strips
`runtime-version.json` (together with contributor docs and bytecode caches)
from the published payload, so installed plugins do not carry internal
repository details.

## Updating

1. Update and test the standalone `agent-scripts` repository.
2. Run the sync script.
3. Review the provenance and vendored diff.
4. Run `xhr-assistant` tests and plugin validation.
5. Release a new plugin version.

Do not run `git pull` or modify files inside an installed plugin runtime. All
runtime changes enter through a reviewed plugin release.
