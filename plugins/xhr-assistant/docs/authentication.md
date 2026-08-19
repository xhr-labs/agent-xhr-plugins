# Authentication and request context

## Problem

`agent-scripts` does not authenticate independently. Under `agent-service`, the
incoming request headers are stored in request-scoped context and serialized to
the child process through `REQUEST_HEADERS`. A native local execution does not
have that context, so it cannot safely reproduce:

- `Authorization`;
- `Xhr-Employee-Id`;
- `Xhr-Company-Id`;
- `Xhr-Groups` and other caller metadata.

This is a core reason why `xhr-assistant` executes through a managed MCP server
instead of the host's local shell.

## Configuration defaults

The default xHR API base URL is:

```text
https://api.x-hr.co
```

It may be overridden for development or staging with `XHR_API_BASE_URL`. The
model cannot override it through tool arguments.

On the first local MCP start, create a user-scoped configuration file if one
does not exist. Example:

```json
{
  "api_base_url": "https://api.x-hr.co",
  "profile_path": "/v1/im/me",
  "active_account": null,
  "company_id": null,
  "employee_id": null,
  "auth": {
    "status": "not_authenticated"
  }
}
```

Recommended locations:

```text
Windows: %APPDATA%\xHR\xhr-assistant\config.json
macOS:   ~/Library/Application Support/xHR/xhr-assistant/config.json
Linux:   ~/.config/xhr-assistant/config.json
```

The configuration file contains settings and identity metadata only. It must
not contain bearer tokens or refresh tokens.

## Selected authentication flow

```text
User generates an access token in xHR Platform
  -> user runs xhr-assistant auth token
  -> CLI validates the token through /v1/im/me
  -> CLI stores the token in the OS credential store
  -> local MCP derives company, employee, user, and group
  -> exec validates the requested leaf operation
  -> exec injects REQUEST_HEADERS and API_BASE_URL
  -> agent-scripts builds RequestContext
  -> xHR API
```

## Trusted context

The MCP runtime owns a request-scoped `ExecutionContext` equivalent to the
context currently used by `agent-service`:

```python
@dataclass(frozen=True)
class ExecutionContext:
    authorization: str
    company_id: str
    employee_id: str
    user_id: str | None
    groups: str | None
    timezone: str | None
    correlation_id: str
```

The exact implementation may use context variables, request state, or an MCP
SDK request context. It must be isolated per request and cleared after tool
execution.

## Header construction

For compatibility with the current runtime, `exec` constructs an allowlisted
header map and serializes it once:

```python
request_headers = {
    "Authorization": context.authorization,
    "Xhr-Company-Id": context.company_id,
    "Xhr-Employee-Id": context.employee_id,
    "X-User-Id": context.user_id,
    "Xhr-Groups": context.groups,
    "X-Timezone": context.timezone,
    "X-Correlation-Id": context.correlation_id,
}

extra_env = {
    "REQUEST_HEADERS": json.dumps(
        {key: value for key, value in request_headers.items() if value}
    ),
    "API_BASE_URL": settings.api_base_url,
}
```

`agent-scripts/src/infrastructure/env/context.py` already lowercases this map
and forwards `Authorization` to its HTTP client, so the initial MCP runtime can
remain backward compatible.

## Identity rules

- The model must not provide authentication headers through `exec.args`.
- The model must not choose `Xhr-Company-Id` or the caller's
  `Xhr-Employee-Id`.
- Any operation acting on another employee uses a business argument such as
  `employee_id`; the server separately checks whether the authenticated caller
  is authorized to act on that employee.
- Header-like keys in `exec.args` are rejected rather than merged.
- The server-configured `API_BASE_URL` cannot be overridden by the model.
- Tokens and identity headers are never returned in tool results or logs.

## Adding a platform-generated token

The current plugin deliberately uses a platform-generated xHR access token. It
does not implement an OAuth browser redirect, authorization-code exchange, or
refresh-token flow. The user creates/revokes tokens in xHR Platform, while the
local stdio MCP owns secure local persistence and request-context construction.

Credential data:

```text
access_token
token_type
```

Store these values in the operating system credential store:

- Windows Credential Manager;
- macOS Keychain;
- Linux Secret Service or another supported system keyring.

Use a stable service name such as `xhr-assistant` and an account identifier
derived after login. Do not log credentials, return them in tool results, or
write them into the plugin directory.

Interactive setup:

```bash
xhr-assistant auth token
```

The short command above is for an editable development installation where the
CLI is on `PATH`. A Windows plugin installation uses its bundled executable —
under Codex:

```powershell
$xhrAssistant = Get-ChildItem "$env:USERPROFILE\.codex\plugins\cache\*\xhr-assistant\*\bin\xhr-assistant.exe" -File |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
& $xhrAssistant.FullName auth token
```

or under Claude Code:

```powershell
$xhrAssistant = Get-ChildItem "$env:USERPROFILE\.claude\plugins\cache\*\xhr-assistant*\bin\xhr-assistant.exe" -File -Recurse |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
& $xhrAssistant.FullName auth token
```

Both hosts resolve the same credential store entry, so one token setup covers
Codex and Claude Code installations on the same machine.

Normally the user should run the exact absolute command included in the MCP
`AUTHENTICATION_REQUIRED` response.

The CLI reads the token with a hidden prompt. It must never accept the token as
a positional command-line argument because arguments can appear in shell
history and process listings.

Non-interactive setup may use standard input:

```bash
printf '%s' "$XHR_AUTHORIZATION" | xhr-assistant auth token --stdin
```

The selected local flow is:

1. `exec` asks the credential store for the active account.
2. If no credential exists, it asks the user to generate a token in xHR
   Platform and run `xhr-assistant auth token`.
3. The CLI accepts the token through a hidden prompt or standard input.
4. The CLI calls `/v1/im/me`; invalid, inactive, or incomplete identities are
   rejected and are not persisted.
5. The CLI saves the validated token in the operating system credential store.
6. The original operation may then be retried.

## Token lifecycle

Before execution, local MCP follows this lifecycle:

```text
load credential
  -> missing: require a platform-generated token
  -> access token valid: continue
  -> /v1/im/me rejects token: require a newly generated token
```

The plugin does not refresh a platform-generated token. When it expires or is
revoked, the user generates a replacement in xHR Platform and runs
`xhr-assistant auth token` again. Importing a replacement atomically updates the
active credential after `/v1/im/me` succeeds.

## Identity resolution

The local MCP resolves the authenticated xHR context from the confirmed profile
endpoint:

```http
GET {XHR_API_BASE_URL}/v1/im/me
Authorization: Bearer <access-token>
Accept: application/json
```

For production, `XHR_API_BASE_URL` defaults to `https://api.x-hr.co`. Sandbox
testing may set it to `https://api.sandbox.x-hr.co`. Browser cookies and browser-
specific headers are not required; the bearer token authenticates this request.

The response contract is:

```json
{
  "data": {
    "user_id": "<user-id>",
    "status": "ACTIVE",
    "group": "ADMIN",
    "company_id": "<company-id>",
    "employee_id": "<employee-id>",
    "roles": []
  }
}
```

The MCP unwraps `data` and constructs trusted execution context as follows:

| Profile field | Runtime value |
| --- | --- |
| `user_id` | active account identifier |
| `company_id` | `Xhr-Company-Id` |
| `employee_id` | `Xhr-Employee-Id` |
| `group` | `Xhr-Groups` (single current group) |
| `status` | must be `ACTIVE` when present |

`Authorization` comes from the stored access token; it is not returned by the
profile endpoint. The MCP combines it with the resolved profile values when it
constructs `REQUEST_HEADERS`.

The model and user never enter company, employee, or group values as trusted
context. The config file may cache them for display and account selection, but
the cache is not an authorization source. The current implementation calls
`/v1/im/me` with the current token before every `exec` and updates the cache.

## Authentication state machine

```text
UNINITIALIZED
  -> create default config
NOT_AUTHENTICATED
  -> add platform-generated token
AUTHENTICATED
  -> resolve and verify xHR identity
READY
  -> allow exec
TOKEN_EXPIRED
  -> generate and add a replacement token
```

The `read` tool may remain available without authentication because it only
returns packaged skill instructions. The `exec` tool requires a complete,
verified execution context before dispatching any script.

## Implemented local components

The current selected flow implements:

- `xhr-assistant auth token` with a hidden prompt;
- `xhr-assistant auth token --stdin` for non-interactive setup;
- validation through `/v1/im/me` before persistence;
- token persistence through the operating system keyring;
- atomic, user-scoped non-secret `config.json` persistence;
- identity resolution through the configurable profile path, defaulting to
  `/v1/im/me`;
- identity is resolved from the current token for every `exec`, so cached
  company, employee, and group metadata is never the authorization source;
- `exec` authentication checks before process creation;
- server-managed `REQUEST_HEADERS` and `API_BASE_URL` injection;
- `auth status` and `auth logout` commands.

OAuth discovery, browser redirects, authorization-code exchange, and refresh
tokens are explicitly outside the current plugin scope. They may be introduced
later for a remote MCP deployment without changing the public `read` and
`exec` tool contracts.

The profile contract accepts the confirmed snake-case fields and retains
camel-case aliases for compatibility. It accepts `group` as the current group
and legacy `groups`/`employee_groups` collections. A generic profile `id` is
not accepted as an employee ID because it may identify the user or profile
rather than the xHR employee record.

## Compatibility target

The first implementation should mirror these existing behaviors:

- request-scoped context equivalent to `request_headers_ctx`;
- `REQUEST_HEADERS` JSON injection performed by `CodeExecutionTool`;
- bearer normalization equivalent to `TurnContextFactory`;
- current `agent-scripts` `AppConfig` and `RequestContext` construction.

A later refactor may call the `agent-scripts` application layer in-process and
pass a typed context directly. The external `read` and `exec` MCP contracts do
not need to change when that refactor happens.
