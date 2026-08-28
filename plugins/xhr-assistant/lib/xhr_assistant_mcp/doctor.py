"""Environment health report for support: `xhr-assistant doctor`.

Read-only. Detects the transition leftovers that have produced confusing
failures in the field (manual config.toml server entries, stale plugin
caches from the pre-per-OS naming, interpreter override variables) and
reports the runtime store state. It never deletes anything — it prints the
exact commands a user can run themselves.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from .runtime import RUNTIME_IMPORT_PROBE, _plugin_base_version, _plugin_root  # noqa: F401


def _codex_home() -> Path:
    return Path(os.getenv("CODEX_HOME", "").strip() or (Path.home() / ".codex"))


def _claude_home() -> Path:
    return Path(os.getenv("CLAUDE_HOME", "").strip() or (Path.home() / ".claude"))


def _check_manual_codex_server(issues: list[dict[str, Any]]) -> None:
    config_path = _codex_home() / "config.toml"
    try:
        content = config_path.read_text(encoding="utf-8")
    except OSError:
        return
    if "[mcp_servers.xhr-assistant]" in content:
        issues.append({
            "issue": "manual_codex_server_entry",
            "detail": (
                f"{config_path} defines [mcp_servers.xhr-assistant] manually. "
                "It shadows the plugin's own server in every project and keeps "
                "running old binaries after upgrades."
            ),
            "fix": f"Remove the [mcp_servers.xhr-assistant] block from {config_path}, then restart your sessions.",
        })


def _check_interpreter_overrides(issues: list[dict[str, Any]]) -> None:
    for name in ("XHR_SCRIPT_PYTHON", "XHR_AGENT_SCRIPTS_ROOT"):
        value = os.getenv(name, "").strip()
        if value:
            issues.append({
                "issue": "override_variable_set",
                "detail": f"{name}={value} overrides the plugin's own runtime resolution.",
                "fix": f"Unset {name} in your shell profile unless you set it deliberately for development.",
            })


def _check_stale_plugin_caches(issues: list[dict[str, Any]], current_name: str) -> None:
    """On mac/linux, a cached plugin under the historical Windows name is a
    leftover from before the per-OS split and carries the wrong launcher."""
    if sys.platform == "win32" or current_name == "xhr-assistant":
        return
    for host_cache in (_codex_home() / "plugins" / "cache", _claude_home() / "plugins" / "cache"):
        if not host_cache.is_dir():
            continue
        for marketplace_dir in host_cache.iterdir():
            stale = marketplace_dir / "xhr-assistant"
            if stale.is_dir():
                issues.append({
                    "issue": "stale_plugin_cache",
                    "detail": f"{stale} is the pre-0.2.0 Windows-named payload and does not run on this OS.",
                    "fix": f"rm -rf \"{stale}\" (and `codex plugin remove xhr-assistant@{marketplace_dir.name}` / the Claude equivalent if still installed)",
                })


def _runtime_key_prefix(current_version: str | None) -> str | None:
    """Store-key prefix this install expects.

    Mirrors the launcher: runtime identity first (shared across plugin
    releases), plugin version only for payloads predating runtime-id.txt.
    """
    try:
        raw = (_plugin_root() / "runtime" / "runtime-id.txt").read_text(encoding="utf-8")
    except OSError:
        raw = ""
    identity = "".join(ch for ch in raw.strip() if ch.isalnum())[:32]
    if identity:
        return f"py-{identity}-"
    return f"{current_version}-" if current_version else None


def _runtime_store_report(current_version: str | None) -> dict[str, Any]:
    store = os.getenv("XHR_RUNTIME_STORE_DIR", "").strip()
    report: dict[str, Any] = {"store_dir": store or None, "entries": [], "stale_entries": []}
    if not store or not Path(store).is_dir():
        return report
    prefix = _runtime_key_prefix(current_version)
    for entry in sorted(Path(store).iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith(".python-bootstrap-"):
            # Staging left behind by a killed launcher; the launcher itself
            # garbage-collects these, so only report the leftovers.
            report["stale_entries"].append(str(entry))
            continue
        report["entries"].append(entry.name)
        if prefix and not entry.name.startswith(prefix):
            report["stale_entries"].append(str(entry))
    return report


def _plugin_name() -> str:
    for manifest_dir in (".codex-plugin", ".claude-plugin"):
        manifest_path = _plugin_root() / manifest_dir / "plugin.json"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        name = str(manifest.get("name", "")).strip()
        if name:
            return name
    return "xhr-assistant"


def run_doctor() -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    current_version = _plugin_base_version()
    current_name = _plugin_name()

    _check_manual_codex_server(issues)
    _check_interpreter_overrides(issues)
    _check_stale_plugin_caches(issues, current_name)

    store = _runtime_store_report(current_version)
    if store["stale_entries"]:
        issues.append({
            "issue": "stale_runtime_store_entries",
            "detail": "Runtime store holds runtimes of older plugin versions (harmless, just disk space).",
            "fix": "Remove them once no old session is running: "
                   + "; ".join(f"rm -rf \"{path}\"" for path in store["stale_entries"]),
        })

    return {
        "status": "ok" if not issues else "issues",
        "plugin": {
            "name": current_name,
            "version": current_version or "unknown",
            "root": str(_plugin_root()),
        },
        "interpreter": sys.executable,
        "runtime_dir": os.getenv("XHR_RUNTIME_DIR", "").strip() or None,
        "runtime_store": store,
        "issues": issues,
    }
