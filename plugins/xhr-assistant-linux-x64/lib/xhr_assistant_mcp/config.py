from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

try:
    from platformdirs import user_config_path
except ImportError:
    def user_config_path(appname: str, appauthor: str | None = None) -> Path:
        if os.name == "nt":
            appdata = os.getenv("APPDATA") or str(Path.home() / "AppData" / "Roaming")
            base = Path(appdata)
            if appauthor:
                base = base / appauthor
            return base / appname
        return Path.home() / ".config" / appname


DEFAULT_API_BASE_URL = "https://api.x-hr.co"
DEFAULT_APP_URL = "https://app.x-hr.co"

# Named environments for `xhr-assistant config set-env`.
ENVIRONMENTS: dict[str, dict[str, str]] = {
    "prod": {
        "api_base_url": DEFAULT_API_BASE_URL,
        "app_url": DEFAULT_APP_URL,
    },
    "sandbox": {
        "api_base_url": "https://api.sandbox.x-hr.co",
        "app_url": "https://sandbox.x-hr.co",
    },
    "dev": {
        "api_base_url": "https://api.dev.x-hr.ai",
        "app_url": "https://dev.x-hr.ai",
    },
}


@dataclass
class AppConfig:
    api_base_url: str = DEFAULT_API_BASE_URL
    app_url: str = DEFAULT_APP_URL
    profile_path: str = "/v1/im/me"
    active_account: str | None = None
    company_id: str | None = None
    employee_id: str | None = None
    groups: list[str] = field(default_factory=list)
    auth_status: str = "not_authenticated"


class ConfigStore:
    def __init__(self, path: Path | None = None) -> None:
        override = os.getenv("XHR_ASSISTANT_CONFIG_FILE", "").strip()
        self.path = path or (
            Path(override)
            if override
            else user_config_path("xhr-assistant", "xHR") / "config.json"
        )

    def load(self) -> AppConfig:
        if not self.path.exists():
            api_base_url = (
                os.getenv("XHR_API_BASE_URL", DEFAULT_API_BASE_URL).strip()
                or DEFAULT_API_BASE_URL
            )
            app_url = (
                os.getenv("XHR_APP_URL", "").strip()
                or _resolve_default_app_url(api_base_url)
            )
            config = AppConfig(
                api_base_url=api_base_url,
                app_url=app_url,
            )
            self.save(config)
            return config
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        oauth_payload = payload.get("oauth") if isinstance(payload.get("oauth"), dict) else {}
        api_base_url = str(payload.get("api_base_url") or DEFAULT_API_BASE_URL)
        app_url = str(payload.get("app_url") or _resolve_default_app_url(api_base_url))
        return AppConfig(
            api_base_url=api_base_url,
            app_url=app_url,
            profile_path=str(
                payload.get("profile_path")
                or oauth_payload.get("profile_path")
                or "/v1/im/me"
            ),
            active_account=_optional_text(payload.get("active_account")),
            company_id=_optional_text(payload.get("company_id")),
            employee_id=_optional_text(payload.get("employee_id")),
            groups=[str(value) for value in payload.get("groups") or []],
            auth_status=str((payload.get("auth") or {}).get("status") or "not_authenticated"),
        )

    def save(self, config: AppConfig) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, Any] = asdict(config)
        payload["auth"] = {"status": payload.pop("auth_status")}
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        temporary.replace(self.path)


def _optional_text(value: object) -> str | None:
    normalized = str(value or "").strip()
    return normalized or None


def _resolve_default_app_url(api_base_url: str) -> str:
    for env_cfg in ENVIRONMENTS.values():
        if env_cfg["api_base_url"] == api_base_url:
            return env_cfg["app_url"]
    return DEFAULT_APP_URL

