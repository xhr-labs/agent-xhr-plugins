from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping


PLACEHOLDER_PATTERN = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")


class SkillTemplateRenderer:
    """Render allowlisted placeholders from the vendored runtime parameters."""

    def __init__(self, runtime_root: Path) -> None:
        self.params_path = runtime_root / "skill-template-params.json"
        self._mtime_ns: int | None = None
        self._params: dict[str, str] = {}

    def render(self, text: str, app_url: str | None = None) -> str:
        if "{{" not in text:
            return text
        params = self._load()

        def replace(match: re.Match[str]) -> str:
            key = match.group(1)
            if key not in params:
                return match.group(0)
            value = params[key]
            if app_url and value.startswith("/"):
                return f"{app_url.rstrip('/')}{value}"
            return value

        return PLACEHOLDER_PATTERN.sub(replace, text)

    def render_data(self, data: Any, app_url: str | None = None) -> Any:
        """Recursively render template placeholders in dict/list/str."""
        if isinstance(data, str):
            return self.render(data, app_url=app_url)
        if isinstance(data, dict):
            return {k: self.render_data(v, app_url=app_url) for k, v in data.items()}
        if isinstance(data, list):
            return [self.render_data(item, app_url=app_url) for item in data]
        return data

    def _load(self) -> dict[str, str]:
        try:
            stat = self.params_path.stat()
        except OSError:
            self._mtime_ns = None
            self._params = {}
            return {}
        if stat.st_mtime_ns == self._mtime_ns:
            return dict(self._params)
        try:
            raw = json.loads(self.params_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            raw = {}
        if not isinstance(raw, Mapping):
            raw = {}
        self._params = {
            key: value
            for key, value in raw.items()
            if isinstance(key, str)
            and re.fullmatch(r"[A-Za-z0-9_]+", key)
            and isinstance(value, str)
        }
        self._mtime_ns = stat.st_mtime_ns
        return dict(self._params)
