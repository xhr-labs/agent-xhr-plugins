from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

from .auth import AuthManager, AuthenticationRequired
from .config import ConfigStore
from .skill_templates import SkillTemplateRenderer


PUBLIC_SKILLS_PREFIX = Path("skills")
SHELL_META = re.compile(r"[;&|><`$()]|\r|\n")
HEADER_ARGUMENTS = {
    "authorization",
    "xhr-authorization",
    "xhr-company-id",
    "xhr-employee-id",
    "xhr-groups",
    "api-base-url",
    "api_base_url",
    "request_headers",
}


class RuntimeContractError(RuntimeError):
    pass


class SkillRuntime:
    def __init__(
        self,
        root: Path | None = None,
        auth_manager: AuthManager | None = None,
        config_store: ConfigStore | None = None,
    ) -> None:
        self.root = (root or _runtime_root()).resolve()
        self.config_store = config_store or ConfigStore()
        self.auth_manager = auth_manager or AuthManager(config_store=self.config_store)
        self.template_renderer = SkillTemplateRenderer(self.root)

    def read(self, path: str) -> dict[str, Any]:
        target = self._resolve_skill_file(path)
        config = self.config_store.load()
        return {
            "status": "success",
            "file_path": str(target),
            "path": _normalize_public_path(path),
            "content": self.template_renderer.render(
                target.read_text(encoding="utf-8"),
                app_url=config.app_url,
            ),
        }

    def exec(
        self,
        command: str | None = None,
        path: str | None = None,
        args: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if command and (path is not None or args is not None):
            raise RuntimeContractError("Use command mode or structured path/args mode, not both.")
        if not command and not path:
            raise RuntimeContractError("exec requires command or path.")
        if command:
            script_public_path, cli_args = self._parse_command(command)
            task_args = None
        else:
            script_public_path = _normalize_public_path(str(path))
            cli_args = []
            task_args = args or {}
            _reject_header_arguments(task_args)

        script = self._resolve_script(script_public_path)
        self._assert_declared_by_leaf(script_public_path)
        try:
            identity = self.auth_manager.resolve_identity()
        except AuthenticationRequired as exc:
            return {
                "status": "error",
                "error": {
                    "code": "AUTHENTICATION_REQUIRED",
                    "message": str(exc),
                    "retryable": True,
                },
                "auth": {
                    "tool": "authenticate",
                    "requires_confirmation": True,
                    "token_input": "private_dialog",
                },
            }

        config = self.config_store.load()
        request_headers = {
            "Authorization": identity.authorization,
            "Xhr-Company-Id": identity.company_id,
            "Xhr-Employee-Id": identity.employee_id,
            "Xhr-Groups": ",".join(identity.groups),
        }
        child_env = _script_environment(self.root)
        child_env.update(
            {
                "API_BASE_URL": config.api_base_url,
                "APP_URL": config.app_url,
                "REQUEST_HEADERS": json.dumps(request_headers),
            }
        )
        interpreter = _script_interpreter()
        if task_args is None:
            argv = [interpreter, "-u", str(script), *cli_args]
            input_text = None
        else:
            launcher = (
                "import json,runpy,sys;"
                "task=json.loads(sys.stdin.read());"
                f"runpy.run_path({str(script)!r},init_globals={{'TASK_ARGS':task}},run_name='__main__')"
            )
            argv = [interpreter, "-u", "-c", launcher]
            input_text = json.dumps(task_args)
        completed = subprocess.run(
            argv,
            cwd=self.root,
            env=child_env,
            input=input_text,
            stdin=subprocess.DEVNULL if input_text is None else None,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=120,
            check=False,
        )
        if completed.returncode != 0:
            return {
                "status": "error",
                "error": {
                    "code": "EXECUTION_FAILED",
                    "message": (completed.stderr or completed.stdout or "Script failed.")[-4000:].strip(),
                    "retryable": False,
                    # Which environment actually ran the script — the decisive
                    # fact when diagnosing import errors from screenshots.
                    "interpreter": interpreter,
                    "plugin_version": _plugin_base_version() or "unknown",
                },
            }
        output = completed.stdout.strip()
        try:
            parsed = json.loads(output)
            return self.template_renderer.render_data(parsed, app_url=config.app_url)
        except json.JSONDecodeError:
            rendered_output = self.template_renderer.render(output, app_url=config.app_url)
            return {"status": "success", "output": rendered_output}

    def _resolve_skill_file(self, path: str) -> Path:
        public = _normalize_public_path(path)
        candidate = self._resolve_public(public)
        if candidate.name != "SKILL.md" or not candidate.is_file():
            raise RuntimeContractError("read accepts only existing skills/**/SKILL.md files.")
        return candidate

    def _resolve_script(self, public_path: str) -> Path:
        candidate = self._resolve_public(public_path)
        parts = Path(public_path).parts
        if "scripts" not in parts or candidate.suffix.lower() != ".py" or not candidate.is_file():
            raise RuntimeContractError("exec accepts only existing Python files under a leaf scripts directory.")
        return candidate

    def _resolve_public(self, public_path: str) -> Path:
        relative = Path(public_path)
        candidate = (self.root / relative).resolve()
        if self.root not in candidate.parents:
            raise RuntimeContractError("The requested path escapes the xHR runtime.")
        return candidate

    def _assert_declared_by_leaf(self, script_public_path: str) -> None:
        script_path = Path(script_public_path)
        scripts_index = script_path.parts.index("scripts")
        leaf_dir = Path(*script_path.parts[:scripts_index])
        leaf_skill = self._resolve_public((leaf_dir / "SKILL.md").as_posix())
        if not leaf_skill.is_file():
            raise RuntimeContractError("The executable target has no leaf SKILL.md.")
        content = leaf_skill.read_text(encoding="utf-8")
        normalized_script = script_path.as_posix()
        if normalized_script not in content and script_path.name not in content:
            raise RuntimeContractError("The target script is not declared by its leaf SKILL.md.")

    def _parse_command(self, command: str) -> tuple[str, list[str]]:
        if SHELL_META.search(command):
            raise RuntimeContractError("Shell composition and redirection are not allowed.")
        tokens = shlex.split(command, posix=True)
        if len(tokens) < 2 or tokens[0].lower() not in {"python", "python3"}:
            raise RuntimeContractError("Command mode accepts only `python skills/.../script.py`.")
        public_path = _normalize_public_path(tokens[1])
        _reject_cli_header_arguments(tokens[2:])
        return public_path, tokens[2:]


def _runtime_root() -> Path:
    override = os.getenv("XHR_AGENT_SCRIPTS_ROOT", "").strip()
    if override:
        return Path(override)
    plugin_root = _plugin_root()
    bundled = plugin_root / "runtime" / "agent-scripts"
    if not bundled.exists():
        raise RuntimeContractError(
            f"The vendored skill tree is missing at {bundled}. If this "
            "session was running while the plugin was upgraded or removed, "
            "the host deleted this plugin version's files — start a new "
            "session to pick up the current version."
        )
    return bundled


def _plugin_base_version() -> str | None:
    """Base semver of the installed plugin, read from a host manifest."""
    for manifest_dir in (".codex-plugin", ".claude-plugin"):
        manifest_path = _plugin_root() / manifest_dir / "plugin.json"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        base = str(manifest.get("version", "")).split("+", 1)[0].strip()
        if base:
            return base
    return None


def _plugin_root() -> Path:
    """Locate the plugin root that carries runtime/agent-scripts.

    The native launcher always exports PLUGIN_ROOT. The parent walk covers
    every direct invocation: it finds the repository root in development
    (src/xhr_assistant_mcp/…) and the installed plugin root when the package
    lives inside the vendored runtime's site-packages
    (runtime/python/…/site-packages/xhr_assistant_mcp/…).
    """
    override = os.getenv("PLUGIN_ROOT", "").strip()
    if override:
        return Path(override).resolve()
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "runtime" / "agent-scripts").is_dir():
            return parent
    return here.parents[2]


# One-line import probe proving an interpreter carries everything leaf
# scripts need: the packages from runtime-requirements.txt plus a working
# IANA timezone database (tzdata on Windows, the OS database elsewhere).
RUNTIME_IMPORT_PROBE = (
    "import httpx, pydantic_settings; from zoneinfo import ZoneInfo; ZoneInfo('UTC')"
)


def _log(message: str) -> None:
    # stdout carries the MCP protocol; diagnostics belong on stderr.
    print(f"[xhr-assistant] {message}", file=sys.stderr)


def _script_interpreter() -> str:
    """Resolve the Python interpreter used to run leaf scripts.

    The MCP server itself runs on the vendored runtime/python interpreter
    (the native launcher in bin/ guarantees it exists before starting the
    server), so leaf scripts run on the very interpreter serving this
    process. XHR_SCRIPT_PYTHON stays as the development override.
    """
    override = os.getenv("XHR_SCRIPT_PYTHON", "").strip()
    if override:
        return override
    return sys.executable


def verify_runtime() -> dict[str, Any]:
    """Check that the active interpreter can run leaf scripts.

    Bootstrap belongs to the native launcher; this is the manual health
    check behind `xhr-assistant setup`.
    """
    interpreter = _script_interpreter()
    try:
        probe = subprocess.run(
            [interpreter, "-c", RUNTIME_IMPORT_PROBE],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "status": "error",
            "interpreter": interpreter,
            "error": f"The interpreter could not be probed: {exc!r}",
        }
    result: dict[str, Any] = {"interpreter": interpreter}
    runtime_dir = os.getenv("XHR_RUNTIME_DIR", "").strip()
    store_dir = os.getenv("XHR_RUNTIME_STORE_DIR", "").strip()
    if runtime_dir:
        result["runtime_dir"] = runtime_dir
    if store_dir:
        result["runtime_store"] = store_dir
    if probe.returncode == 0:
        return {"status": "ok", **result}
    return {
        "status": "error",
        **result,
        "error": (probe.stderr or probe.stdout or "Import probe failed.")[-2000:].strip(),
    }


def _script_environment(runtime_root: Path) -> dict[str, str]:
    """Build the leaf-script environment.

    The runtime root goes on PYTHONPATH so leaf scripts resolve `src.*`
    imports in command mode, where sys.path starts at the leaf scripts
    directory instead of the runtime root.
    """
    child_env = os.environ.copy()
    existing = child_env.get("PYTHONPATH", "")
    child_env["PYTHONPATH"] = (
        f"{runtime_root}{os.pathsep}{existing}" if existing else str(runtime_root)
    )
    # Piped stdout defaults to the ANSI code page on Windows, which cannot
    # encode the non-ASCII output that leaf scripts emit (ensure_ascii=False).
    child_env["PYTHONIOENCODING"] = "utf-8"
    # The launcher scrubs PYTHONHOME before the server starts; repeating the
    # defense covers development runs without the launcher, where an outer
    # tool chain (uv trampolines, conda) may export it and point the child
    # interpreter at a foreign stdlib.
    child_env.pop("PYTHONHOME", None)
    return child_env


def _normalize_public_path(path: str) -> str:
    normalized = path.replace("\\", "/").strip().lstrip("./")
    parts = Path(normalized).parts
    if not parts or parts[0] != PUBLIC_SKILLS_PREFIX.as_posix() or ".." in parts:
        raise RuntimeContractError("Paths must be runtime-relative under skills/.")
    return Path(*parts).as_posix()


def _reject_header_arguments(args: dict[str, Any]) -> None:
    invalid = {str(key).lower().replace("_", "-") for key in args} & {
        key.replace("_", "-") for key in HEADER_ARGUMENTS
    }
    if invalid:
        raise RuntimeContractError("Authentication and tenant headers are server-managed.")


def _reject_cli_header_arguments(args: list[str]) -> None:
    for arg in args:
        key = arg.split("=", 1)[0].lstrip("-").lower().replace("_", "-")
        if key in {value.replace("_", "-") for value in HEADER_ARGUMENTS}:
            raise RuntimeContractError("Authentication and tenant headers are server-managed.")
