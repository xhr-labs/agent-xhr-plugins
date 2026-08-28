from typing import AsyncContextManager, Protocol


class HttpClient(Protocol):
    def session(self) -> AsyncContextManager:
        ...

