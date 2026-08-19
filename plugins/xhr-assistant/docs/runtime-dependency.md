# Vendored runtime strategy

## Decision

`xhr-assistant` ships two vendored runtimes:

- `runtime/agent-scripts`: a snapshot of the `agent-scripts` skill tree. The
  installed plugin does not require a Git submodule, a sibling repository, or
  a runtime clone.
- `runtime/python`: a relocatable CPython distribution
  (python-build-standalone) with the packages from `runtime-requirements.txt`
  preinstalled. MCP `exec` runs leaf scripts with this interpreter because the
  frozen MCP binary cannot execute Python source itself and installed machines
  cannot be assumed to have Python with the right dependencies.

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

For development and tests, `XHR_SCRIPT_PYTHON` overrides the interpreter used
by `exec`; an editable (non-frozen) install defaults to the current
interpreter.

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
