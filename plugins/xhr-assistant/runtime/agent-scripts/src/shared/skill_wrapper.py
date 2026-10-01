from __future__ import annotations

import asyncio
import importlib
import json
import sys
from typing import Any

from src.infrastructure.di.singleton_container import container

from .task_args_cli import resolve_task_args


def _ensure_utf8_stdio() -> None:
    """Force UTF-8 stdio so results survive legacy Windows codepages (e.g. cp1252)."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        encoding = getattr(stream, "encoding", None)
        if reconfigure and encoding and encoding.lower() not in ("utf-8", "utf8"):
            reconfigure(encoding="utf-8")


def run_skill_entry(
    app_module_name: str,
    argument_specs: list[dict[str, Any]],
    injected_task_args: dict[str, Any] | None = None,
) -> None:
    """Execute a skill wrapper with shared TASK_ARGS/CLI resolution.

    This keeps leaf wrappers thin while supporting both CLI flags and direct TASK_ARGS
    injection through the shared runtime surface.
    """
    _ensure_utf8_stdio()
    rejection = _reject_unknown_injected_args(argument_specs, injected_task_args)
    if rejection is not None:
        print(json.dumps(rejection, ensure_ascii=False))
        return
    task_args = resolve_task_args(argument_specs, injected_task_args=injected_task_args)
    context = container.get_request_context()
    http_client = container.get_http_client()
    tool = importlib.import_module(app_module_name)
    result = asyncio.run(tool.run(task_args, context, http_client))

    if result is not None:
        print(json.dumps(result, ensure_ascii=False))


def _reject_unknown_injected_args(
    argument_specs: list[dict[str, Any]],
    injected_task_args: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Fail fast when the runtime injects flags the wrapper never declared.

    The agent runtime parses `--any-flag value` into TASK_ARGS generically, so a mistyped flag
    (``--search-term``, ``--help``) would otherwise be silently dropped and the script would run an
    unfiltered call that the model then trusts.
    """
    if not isinstance(injected_task_args, dict) or not argument_specs:
        return None
    known = {spec["dest"] for spec in argument_specs}
    flags = ", ".join(spec["flag"] for spec in argument_specs)
    if "help" in injected_task_args:
        return {"ok": False, "error": f"help: supported flags are {flags}. Read the leaf SKILL.md for value formats."}
    unknown = sorted(key for key in injected_task_args if key not in known)
    if not unknown:
        return None
    return {
        "ok": False,
        "error": f"unknown_args: {', '.join('--' + key.replace('_', '-') for key in unknown)}. Supported flags: {flags}.",
    }
