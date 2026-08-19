from __future__ import annotations

from typing import Any


class FetchJsonError(Exception):
    def __init__(self, status_code: int | None, payload: Any):
        self.status_code = status_code
        self.payload = payload
        super().__init__(self._build_message())

    def _build_message(self) -> str:
        if isinstance(self.payload, dict):
            message = self.payload.get("message")
            if message:
                return str(message)
        if self.payload in (None, ""):
            return "Request failed"
        return str(self.payload)

    def as_error(self):
        if isinstance(self.payload, dict):
            return self.payload
        if self.payload in (None, ""):
            return {"message": "Request failed"}
        return {"message": str(self.payload)}


async def fetch_json(client, url: str, method: str = "GET", **kwargs: Any):
    """
    Safe async httpx helper:
    - fully closes response
    - avoids anyio AsyncExitStack warnings
    - raises FetchJsonError on backend failure with payload passthrough
    """
    request_method = (method or "GET").upper()
    response = await client.request(request_method, url, **kwargs)
    try:
        try:
            payload = response.json()
        except Exception:
            payload = {}
        if response.status_code >= 400:
            raise FetchJsonError(response.status_code, payload)
        return payload
    finally:
        await response.aclose()


async def request_json(client, method: str, url: str, **kwargs: Any) -> tuple[int, Any]:
    """
    Safe async HTTP request returning (status_code, payload) tuple without raising exception on 4xx/5xx.
    Useful when status code multi-status / status inspection is required.
    """
    request_method = (method or "GET").upper()
    response = await client.request(request_method, url, **kwargs)
    try:
        try:
            payload = response.json()
        except Exception:
            payload = {}
        return response.status_code, payload
    finally:
        await response.aclose()


def format_error(payload: Any = None, exc: Exception | None = None) -> dict[str, Any]:
    """Format error payload or exception into standard error dict."""
    if exc is not None:
        return {"message": str(exc)}
    if isinstance(payload, dict):
        return payload
    if payload in (None, ""):
        return {"message": "Request failed"}
    return {"message": str(payload)}
