from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone

import keyring
from keyring.errors import KeyringError


SERVICE_NAME = "xhr-assistant"


class CredentialStoreError(RuntimeError):
    pass


@dataclass(frozen=True)
class TokenSet:
    access_token: str
    refresh_token: str | None = None
    expires_at: float | None = None
    token_type: str = "Bearer"
    scopes: list[str] | None = None

    def is_expired(self, skew_seconds: int = 60) -> bool:
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc).timestamp() + skew_seconds >= self.expires_at


class CredentialStore:
    def load(self, account: str) -> TokenSet | None:
        try:
            raw = keyring.get_password(SERVICE_NAME, account)
        except KeyringError as exc:
            raise CredentialStoreError(f"Unable to read the OS credential store: {exc}") from exc
        if not raw:
            return None
        payload = json.loads(raw)
        return TokenSet(
            access_token=str(payload["access_token"]),
            refresh_token=_optional_text(payload.get("refresh_token")),
            expires_at=float(payload["expires_at"]) if payload.get("expires_at") else None,
            token_type=str(payload.get("token_type") or "Bearer"),
            scopes=[str(value) for value in payload.get("scopes") or []],
        )

    def save(self, account: str, token: TokenSet) -> None:
        try:
            keyring.set_password(SERVICE_NAME, account, json.dumps(asdict(token)))
        except KeyringError as exc:
            raise CredentialStoreError(f"Unable to write the OS credential store: {exc}") from exc

    def delete(self, account: str) -> None:
        try:
            keyring.delete_password(SERVICE_NAME, account)
        except keyring.errors.PasswordDeleteError:
            return
        except KeyringError as exc:
            raise CredentialStoreError(f"Unable to update the OS credential store: {exc}") from exc


def _optional_text(value: object) -> str | None:
    normalized = str(value or "").strip()
    return normalized or None
