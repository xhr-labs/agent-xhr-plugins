from __future__ import annotations

import os
import subprocess
import sys
from typing import Any

from .config import ConfigStore


def authenticate() -> dict[str, Any]:
    command = _dialog_command()
    kwargs: dict[str, Any] = {}
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    completed = subprocess.run(command, check=False, **kwargs)
    config = ConfigStore().load()
    if completed.returncode == 0 and config.auth_status == "authenticated":
        return {
            "status": "authenticated",
            "account": config.active_account,
            "company_id": config.company_id,
            "employee_id": config.employee_id,
        }
    if completed.returncode == 2:
        return {"status": "cancelled"}
    if completed.returncode == 3:
        token_command = " ".join(_token_command())
        return {
            "status": "error",
            "error": {
                "code": "AUTH_DIALOG_UNAVAILABLE",
                "message": (
                    "No graphical display is available for the xHR authentication "
                    "window. Ask the user to generate an access token in xHR "
                    f"Platform, run `{token_command}` in their own terminal, paste "
                    "the token into the hidden prompt, and then retry the original "
                    "request. Never collect the token in chat."
                ),
                "retryable": True,
            },
            "auth": {
                "cli_command": _token_command(),
                "token_input": "hidden_prompt",
            },
        }
    return {
        "status": "error",
        "error": {
            "code": "AUTHENTICATION_FAILED",
            "message": "The xHR authentication window closed without completing authentication.",
            "retryable": True,
        },
    }


def _dialog_command() -> list[str]:
    # The server runs on the vendored (or development) interpreter, and the
    # dialog runs on the same one. CREATE_NO_WINDOW above keeps the child
    # console hidden on Windows; the tkinter window still shows.
    return [sys.executable, "-m", "xhr_assistant_mcp.cli", "auth", "dialog"]


def _token_command() -> list[str]:
    return [sys.executable, "-m", "xhr_assistant_mcp.cli", "auth", "token"]
