from __future__ import annotations

import argparse
import getpass
import json
import sys

from .auth import AuthManager
from .config import ENVIRONMENTS, ConfigStore


def main() -> None:
    parser = argparse.ArgumentParser(prog="xhr-assistant")
    subparsers = parser.add_subparsers(dest="group", required=True)
    subparsers.add_parser("mcp")
    subparsers.add_parser(
        "setup",
        help=(
            "Verify the Python runtime health (the launcher in bin/ installs "
            "the runtime automatically)."
        ),
    )
    subparsers.add_parser(
        "doctor",
        help=(
            "Read-only environment health report: flags leftover manual "
            "server entries, stale caches, override variables, and old "
            "runtime store entries, with the exact cleanup commands."
        ),
    )
    install_parser = subparsers.add_parser(
        "install", help="Register this plugin with an agent host."
    )
    install_parser.add_argument("host", choices=["antigravity"])
    uninstall_parser = subparsers.add_parser(
        "uninstall", help="Remove this plugin's registration from an agent host."
    )
    uninstall_parser.add_argument("host", choices=["antigravity"])
    config_parser = subparsers.add_parser(
        "config", help="Inspect or change the xHR environment this plugin targets."
    )
    config_subparsers = config_parser.add_subparsers(dest="action", required=True)
    set_env = config_subparsers.add_parser(
        "set-env", help="Point the plugin at a named xHR environment."
    )
    set_env.add_argument("environment", choices=sorted(ENVIRONMENTS))
    set_url = config_subparsers.add_parser(
        "set-url", help="Point the plugin at a custom xHR API base URL."
    )
    set_url.add_argument("url")
    set_app_url = config_subparsers.add_parser(
        "set-app-url", help="Point the plugin at a custom xHR App (frontend) URL."
    )
    set_app_url.add_argument("url")
    config_subparsers.add_parser("show", help="Print the active environment.")
    auth_parser = subparsers.add_parser("auth")
    auth_subparsers = auth_parser.add_subparsers(dest="action", required=True)
    token = auth_subparsers.add_parser("token")
    token.add_argument(
        "--stdin",
        action="store_true",
        help="Read the token from standard input instead of a hidden prompt.",
    )
    auth_subparsers.add_parser("status")
    auth_subparsers.add_parser("logout")
    auth_subparsers.add_parser("dialog", help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.group == "mcp":
        from .server import main as run_mcp

        run_mcp()
        return

    if args.group == "setup":
        from .runtime import verify_runtime

        result = verify_runtime()
        print(json.dumps(result, indent=2))
        if result["status"] != "ok":
            raise SystemExit(1)
        return

    if args.group == "doctor":
        from .doctor import run_doctor

        result = run_doctor()
        print(json.dumps(result, indent=2))
        if result["status"] != "ok":
            raise SystemExit(1)
        return

    if args.group in ("install", "uninstall"):
        from .install_antigravity import install, uninstall

        result = install() if args.group == "install" else uninstall()
        print(json.dumps(result, indent=2))
        return

    if args.group == "config":
        _run_config(args)
        return

    manager = AuthManager()
    if args.action == "dialog":
        # Exit code 3 signals "no dialog possible here" (missing tkinter or no
        # display); the MCP authenticate tool maps it to CLI guidance.
        try:
            from .auth_dialog import run_auth_dialog
        except Exception as exc:
            print(f"The xHR authentication dialog cannot start: {exc}", file=sys.stderr)
            raise SystemExit(3) from exc
        try:
            raise SystemExit(run_auth_dialog(manager))
        except SystemExit:
            raise
        except Exception as exc:
            print(f"The xHR authentication dialog cannot start: {exc}", file=sys.stderr)
            raise SystemExit(3) from exc
    if args.action == "token":
        raw_token = sys.stdin.read().strip() if args.stdin else getpass.getpass("xHR access token: ")
        identity = manager.import_token(raw_token)
        print(json.dumps({"status": "authenticated", "account": identity.account}, indent=2))
    elif args.action == "logout":
        manager.logout()
        print(json.dumps({"status": "not_authenticated"}))
    else:
        config = ConfigStore().load()
        print(
            json.dumps(
                {
                    "status": config.auth_status,
                    "account": config.active_account,
                    "company_id": config.company_id,
                    "employee_id": config.employee_id,
                    "api_base_url": config.api_base_url,
                    "app_url": config.app_url,
                    "config_file": str(ConfigStore().path),
                },
                indent=2,
            )
        )


def _run_config(args: argparse.Namespace) -> None:
    store = ConfigStore()
    config = store.load()
    if args.action == "show":
        environment = next(
            (
                name
                for name, env_cfg in ENVIRONMENTS.items()
                if env_cfg["api_base_url"] == config.api_base_url
                and env_cfg["app_url"] == config.app_url
            ),
            "custom",
        )
        print(
            json.dumps(
                {
                    "environment": environment,
                    "api_base_url": config.api_base_url,
                    "app_url": config.app_url,
                    "auth_status": config.auth_status,
                    "account": config.active_account,
                    "config_file": str(store.path),
                },
                indent=2,
            )
        )
        return

    if args.action == "set-env":
        env_cfg = ENVIRONMENTS[args.environment]
        api_url = env_cfg["api_base_url"]
        app_url = env_cfg["app_url"]
        changed = (api_url != config.api_base_url) or (app_url != config.app_url)
        config.api_base_url = api_url
        config.app_url = app_url
        # Identity and tokens are environment-specific; force a fresh sign-in.
        config.active_account = None
        config.company_id = None
        config.employee_id = None
        config.groups = []
        config.auth_status = "not_authenticated"
        store.save(config)
        print(
            json.dumps(
                {
                    "status": "updated" if changed else "unchanged",
                    "api_base_url": api_url,
                    "app_url": app_url,
                    "note": (
                        "Restart the agent session and authenticate again with a "
                        "token generated on this environment."
                    ),
                },
                indent=2,
            )
        )
        return

    if args.action == "set-url":
        url = args.url.strip().rstrip("/")
        if not url.startswith(("https://", "http://")):
            raise SystemExit(f"Not an HTTP(S) URL: {args.url}")
        changed = url != config.api_base_url
        config.api_base_url = url
        # Identity and tokens are environment-specific; force a fresh sign-in.
        config.active_account = None
        config.company_id = None
        config.employee_id = None
        config.groups = []
        config.auth_status = "not_authenticated"
        store.save(config)
        print(
            json.dumps(
                {
                    "status": "updated" if changed else "unchanged",
                    "api_base_url": url,
                    "note": (
                        "Restart the agent session and authenticate again with a "
                        "token generated on this environment."
                    ),
                },
                indent=2,
            )
        )
        return

    if args.action == "set-app-url":
        url = args.url.strip().rstrip("/")
        if not url.startswith(("https://", "http://")):
            raise SystemExit(f"Not an HTTP(S) URL: {args.url}")
        changed = url != config.app_url
        config.app_url = url
        store.save(config)
        print(
            json.dumps(
                {
                    "status": "updated" if changed else "unchanged",
                    "app_url": url,
                },
                indent=2,
            )
        )
        return


if __name__ == "__main__":
    main()
