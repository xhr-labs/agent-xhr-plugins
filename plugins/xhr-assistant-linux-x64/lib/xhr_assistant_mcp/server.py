from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from .auth_launcher import authenticate
from .runtime import RuntimeContractError, SkillRuntime


mcp = FastMCP("xHR Assistant")
runtime = SkillRuntime()


@mcp.tool(name="read", annotations={"readOnlyHint": True})
def read_tool(path: str) -> dict[str, Any]:
    """Read an approved runtime-relative xHR skills/**/SKILL.md file."""
    try:
        return runtime.read(path)
    except RuntimeContractError as exc:
        return _contract_error(exc)


@mcp.tool(name="exec")
def exec_tool(
    command: str | None = None,
    path: str | None = None,
    args: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute a script declared by an xHR leaf skill using command or structured mode."""
    try:
        return runtime.exec(command=command, path=path, args=args)
    except RuntimeContractError as exc:
        return _contract_error(exc)


@mcp.tool(name="authenticate", annotations={"readOnlyHint": False, "openWorldHint": True})
def authenticate_tool() -> dict[str, Any]:
    """Open the private xHR token dialog and store verified credentials outside the agent host."""
    return authenticate()


def _contract_error(exc: Exception) -> dict[str, Any]:
    return {
        "status": "error",
        "error": {
            "code": "INVALID_TOOL_REQUEST",
            "message": str(exc),
            "retryable": False,
        },
    }


def main() -> None:
    mcp.run(transport="stdio", show_banner=False)


if __name__ == "__main__":
    main()
