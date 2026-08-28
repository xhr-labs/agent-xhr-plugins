"""Register the plugin with Google Antigravity (IDE and agy CLI).

Antigravity ingests customizations from the global root ``~/.gemini/config``:
a plugin bundle at ``plugins/<name>/`` carrying ``plugin.json``,
``mcp_config.json``, and ``skills/`` is loaded automatically by the IDE, the
agy CLI, and the SDK (per the built-in agy-customizations guide).
``xhr-assistant install antigravity`` builds that bundle with the binary's
absolute path and the native router skills; re-running it after moving or
updating the plugin refreshes everything.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

from .runtime import _plugin_root

SERVER_NAME = "xhr-assistant"


def _gemini_home() -> Path:
    override = os.getenv("XHR_GEMINI_HOME", "").strip()
    if override:
        return Path(override)
    return Path.home() / ".gemini"


def _config_root() -> Path:
    return _gemini_home() / "config"


def _bundle_dir() -> Path:
    return _config_root() / "plugins" / SERVER_NAME


def _server_command() -> tuple[str, list[str]]:
    """Register the native launcher when installed, the interpreter in dev.

    The launcher guarantees the vendored runtime exists and scrubs the
    environment before the server starts, so installed registrations must go
    through it rather than the interpreter directly.
    """
    launcher_name = "xhr-assistant.exe" if os.name == "nt" else "xhr-assistant"
    launcher = _plugin_root() / "bin" / launcher_name
    if launcher.is_file():
        return str(launcher.resolve()), ["mcp"]
    return sys.executable, ["-m", "xhr_assistant_mcp.cli", "mcp"]


def _plugin_version() -> str:
    manifest = _plugin_root() / ".claude-plugin" / "plugin.json"
    try:
        return str(json.loads(manifest.read_text(encoding="utf-8"))["version"])
    except (OSError, ValueError, KeyError):
        return "0.0.0"


def _plugin_skills() -> list[Path]:
    skills_root = _plugin_root() / "skills"
    if not skills_root.is_dir():
        raise SystemExit(f"No skills directory found at {skills_root}.")
    return sorted(
        entry
        for entry in skills_root.iterdir()
        if entry.is_dir() and (entry / "SKILL.md").is_file()
    )


def install() -> dict[str, Any]:
    bundle = _bundle_dir()
    if bundle.exists():
        shutil.rmtree(bundle)
    (bundle / "skills").mkdir(parents=True)

    command, args = _server_command()
    (bundle / "plugin.json").write_text(
        json.dumps(
            {
                "name": SERVER_NAME,
                "version": _plugin_version(),
                "description": (
                    "Native xHR domain skills backed by managed read and exec MCP tools."
                ),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (bundle / "mcp_config.json").write_text(
        json.dumps(
            {"mcpServers": {SERVER_NAME: {"command": command, "args": args}}}, indent=2
        )
        + "\n",
        encoding="utf-8",
    )
    installed = []
    for skill_dir in _plugin_skills():
        shutil.copytree(skill_dir, bundle / "skills" / skill_dir.name)
        installed.append(skill_dir.name)

    legacy = _remove_legacy_skills()
    mcp_actions = _sync_global_mcp_config(command, args)

    return {
        "status": "installed",
        "plugin_bundle": str(bundle),
        "server_command": [command, *args],
        "skills_installed": installed,
        "legacy_cleanup": legacy,
        "mcp_config": mcp_actions,
    }


def uninstall() -> dict[str, Any]:
    bundle = _bundle_dir()
    removed = bundle.exists()
    if removed:
        shutil.rmtree(bundle)
    legacy = _remove_legacy_skills()
    mcp_actions = _remove_from_global_mcp_config()
    return {
        "status": "uninstalled",
        "plugin_bundle": str(bundle),
        "bundle_removed": removed,
        "legacy_cleanup": legacy,
        "mcp_cleanup": mcp_actions,
    }


def _sync_global_mcp_config(command: str, args: list[str]) -> list[str]:
    """Register or update the server in the global ~/.gemini/config/mcp_config.json."""
    actions: list[str] = []
    global_config = _config_root() / "mcp_config.json"
    global_config.parent.mkdir(parents=True, exist_ok=True)
    config: dict[str, Any] = {}
    if global_config.exists():
        try:
            config = json.loads(global_config.read_text(encoding="utf-8") or "{}")
        except json.JSONDecodeError:
            config = {}
    if not isinstance(config, dict):
        config = {}
    servers = config.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        servers = {}
        config["mcpServers"] = servers
    servers[SERVER_NAME] = {"command": command, "args": args}
    temporary = global_config.with_suffix(".tmp")
    temporary.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    temporary.replace(global_config)
    actions.append(f"registered {SERVER_NAME} in {global_config}")
    return actions


def _remove_from_global_mcp_config() -> list[str]:
    """Remove the server from the global ~/.gemini/config/mcp_config.json."""
    actions: list[str] = []
    global_config = _config_root() / "mcp_config.json"
    if global_config.exists():
        try:
            config = json.loads(global_config.read_text(encoding="utf-8") or "{}")
        except json.JSONDecodeError:
            return actions
        servers = config.get("mcpServers")
        if isinstance(servers, dict) and SERVER_NAME in servers:
            del servers[SERVER_NAME]
            temporary = global_config.with_suffix(".tmp")
            temporary.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
            temporary.replace(global_config)
            actions.append(f"removed {SERVER_NAME} from {global_config}")
    return actions


def _remove_legacy_skills() -> list[str]:
    """Remove legacy skill directories written by pre-0.1.14 installers."""
    actions: list[str] = []
    legacy_skills_root = _gemini_home() / "skills"
    for skill_dir in _plugin_skills():
        legacy_copy = legacy_skills_root / skill_dir.name
        if legacy_copy.exists():
            shutil.rmtree(legacy_copy)
            actions.append(f"removed {legacy_copy}")
    return actions
