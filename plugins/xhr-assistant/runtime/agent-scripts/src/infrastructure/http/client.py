from contextlib import asynccontextmanager

import httpx


class AsyncHttpClient:
    def __init__(self, timeout: float = 30.0) -> None:
        self._timeout = timeout

    @asynccontextmanager
    async def session(self) -> httpx.AsyncClient:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            yield client

