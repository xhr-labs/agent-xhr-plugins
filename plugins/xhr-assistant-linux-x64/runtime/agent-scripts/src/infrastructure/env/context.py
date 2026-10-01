import json
from typing import Any, Dict

from src.config.app_config import AppConfig
from src.core.models.request_context import RequestContext


def _load_request_headers(raw_headers: str) -> Dict[str, Any]:
    try:
        headers = json.loads(raw_headers or "{}")
    except Exception:
        return {}
    if not isinstance(headers, dict):
        return {}
    return {
        str(key).lower(): value
        for key, value in headers.items()
        if key is not None and value is not None
    }


def build_request_context(config: AppConfig) -> RequestContext:
    request_headers = _load_request_headers(config.REQUEST_HEADERS)
    api_base_url = config.API_BASE_URL
    headers = {
        "Authorization": request_headers.get("authorization"),
        "Content-Type": "application/json",
    }
    headers = {key: value for key, value in headers.items() if value is not None}
    return RequestContext(
        api_base_url=api_base_url,
        request_headers=request_headers,
        headers=headers,
    )

