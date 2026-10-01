from src.config.app_config import AppConfig
from src.infrastructure.env.context import build_request_context
from src.infrastructure.http.client import AsyncHttpClient


class Container:
    def __init__(self) -> None:
        self._config = AppConfig()
        self._http_client = AsyncHttpClient()

    def get_request_context(self):
        return build_request_context(self._config)

    def get_config(self) -> AppConfig:
        return self._config

    def get_http_client(self) -> AsyncHttpClient:
        return self._http_client

