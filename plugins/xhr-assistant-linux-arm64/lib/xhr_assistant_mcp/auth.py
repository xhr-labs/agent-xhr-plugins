from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx

from .config import AppConfig, ConfigStore
from .credentials import CredentialStore, TokenSet


class AuthenticationRequired(RuntimeError):
    pass


@dataclass(frozen=True)
class ExecutionIdentity:
    authorization: str
    company_id: str
    employee_id: str
    groups: list[str]
    account: str


class AuthManager:
    def __init__(
        self,
        config_store: ConfigStore | None = None,
        credential_store: CredentialStore | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.config_store = config_store or ConfigStore()
        self.credential_store = credential_store or CredentialStore()
        # The xHR API gateway rejects requests without a JSON content type
        # (415 Unsupported Media Type), even for GET.
        self.client = client or httpx.Client(
            timeout=30,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )

    def resolve_identity(self) -> ExecutionIdentity:
        config = self.config_store.load()
        if not config.active_account:
            raise AuthenticationRequired(
                "No active xHR account. Run the `auth token` command returned by xHR Assistant."
            )
        token = self.credential_store.load(config.active_account)
        if token is None:
            raise AuthenticationRequired(
                "xHR credentials are missing. Run the `auth token` command returned by xHR Assistant."
            )
        if token.is_expired():
            raise AuthenticationRequired(
                "The xHR access token expired. Generate a new token on xHR Platform and run "
                "the `auth token` command returned by xHR Assistant."
            )
        # Identity and tenant scope are security-sensitive and must be resolved
        # from the current verified token rather than trusted from local cache.
        config = self._resolve_profile(config, token)
        if not config.company_id or not config.employee_id:
            raise AuthenticationRequired("The authenticated xHR identity is incomplete.")
        return ExecutionIdentity(
            authorization=f"{token.token_type} {token.access_token}",
            company_id=config.company_id,
            employee_id=config.employee_id,
            groups=config.groups,
            account=config.active_account,
        )

    def import_token(self, raw_token: str) -> ExecutionIdentity:
        access_token = raw_token.strip()
        if access_token.lower().startswith("bearer "):
            access_token = access_token[7:].strip()
        if not access_token:
            raise AuthenticationRequired("An xHR access token is required.")

        config = self.config_store.load()
        token = TokenSet(access_token=access_token)
        profile = self._fetch_profile(config, token)
        _apply_profile(config, profile)
        if not config.company_id or not config.employee_id:
            raise AuthenticationRequired("The authenticated xHR identity is incomplete.")
        account = _first_text(profile, "user_id", "email", "employee_id")
        if not account:
            raise AuthenticationRequired("The xHR profile did not provide an account identifier.")

        self.credential_store.save(account, token)
        config.active_account = account
        config.auth_status = "authenticated"
        self.config_store.save(config)
        return self.resolve_identity()

    def logout(self) -> None:
        config = self.config_store.load()
        if config.active_account:
            self.credential_store.delete(config.active_account)
        config.active_account = None
        config.company_id = None
        config.employee_id = None
        config.groups = []
        config.auth_status = "not_authenticated"
        self.config_store.save(config)

    def _resolve_profile(self, config: AppConfig, token: TokenSet) -> AppConfig:
        try:
            profile = self._fetch_profile(config, token)
        except (httpx.HTTPError, ValueError, json.JSONDecodeError) as exc:
            raise AuthenticationRequired(
                "The current xHR identity could not be verified. Sign in again."
            ) from exc
        _apply_profile(config, profile)
        self.config_store.save(config)
        return config

    def _fetch_profile(self, config: AppConfig, token: TokenSet) -> dict[str, Any]:
        url = f"{config.api_base_url.rstrip('/')}/{config.profile_path.lstrip('/')}"
        response = self.client.get(
            url,
            headers={"Authorization": f"{token.token_type} {token.access_token}"},
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise AuthenticationRequired("The xHR profile response was not an object.")
        data = payload.get("data")
        return data if isinstance(data, dict) else payload


def _apply_profile(config: AppConfig, profile: dict[str, Any]) -> None:
    status = _first_text(profile, "status")
    if status and status.upper() != "ACTIVE":
        raise AuthenticationRequired(f"The authenticated xHR account is {status}, not ACTIVE.")
    config.company_id = _first_text(profile, "company_id", "companyId", "xhr_company_id")
    config.employee_id = _first_text(profile, "employee_id", "employeeId")
    groups = profile.get("groups") or profile.get("employee_groups") or profile.get("group") or []
    if isinstance(groups, str):
        config.groups = [part.strip() for part in groups.split(",") if part.strip()]
    elif isinstance(groups, list):
        config.groups = [str(value) for value in groups]


def _first_text(payload: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = str(payload.get(key) or "").strip()
        if value:
            return value
    return None
