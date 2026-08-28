from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class RequestContext:
    api_base_url: str
    request_headers: Dict[str, Any]
    headers: Dict[str, str]

