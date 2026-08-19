# MCP tool contracts

The MCP server exposes exactly three public tools named `read`, `exec`, and
`authenticate`.

## `read`

Input:

```json
{
  "path": "skills/timeoff/submit_my_leave_request/SKILL.md"
}
```

Output:

```json
{
  "status": "success",
  "file_path": "<resolved server-side path>",
  "path": "skills/timeoff/submit_my_leave_request/SKILL.md",
  "content": "<rendered SKILL.md content>"
}
```

Compatibility requirements:

- mirror `FileIOTool.read` from `agent-service`;
- accept only runtime-relative `skills/**/SKILL.md` paths;
- reject absolute paths, traversal, symlink escape, and non-skill files;
- render supported skill templates before returning content.

The implementation loads allowlisted string values from the vendored
`skill-template-params.json`, caches them by file modification time, replaces
known `{{name}}` placeholders, and leaves unknown placeholders unchanged.

## `exec`

`exec` supports the same two mutually exclusive modes as `agent-service`.

Command mode:

```json
{
  "command": "python skills/timeoff/get_timeoff_types/scripts/get_timeoff_types.py"
}
```

Structured mode:

```json
{
  "path": "skills/timeoff/get_timeoff_types/scripts/get_timeoff_types.py",
  "args": {}
}
```

The server rejects payloads that mix `command` with `path` or `args`.

Security requirements:

- `exec` is not a general-purpose shell;
- targets must resolve beneath `skills/<domain>/<leaf>/scripts/`;
- the selected leaf must explicitly declare the target script;
- command mode must reject shell composition, redirection, substitution, and
  unsupported executables;
- structured `args` must remain a native object;
- stdout contains one structured JSON result and diagnostics go to server logs;
- side-effect, retry, idempotency, authentication, and authorization behavior
  mirrors `agent-service`.

Before starting the approved script, `exec` injects server-derived context:

```text
REQUEST_HEADERS=<JSON object containing trusted request headers>
API_BASE_URL=<server-configured xHR API base URL>
```

Neither command mode nor structured mode accepts credentials, company identity,
or caller identity as model-controlled arguments.

If no usable authentication context can be resolved, `exec` returns a stable
authentication error without starting the target script:

```json
{
  "status": "error",
  "error": {
    "code": "AUTHENTICATION_REQUIRED",
    "message": "Add an xHR Platform token before running this operation.",
    "retryable": true
  },
  "auth": {
    "command": "xhr-assistant auth token"
  }
}
```

The implemented local challenge returns the explicit command
`xhr-assistant auth token`. The user first generates a token in xHR Platform.
After the CLI validates it through `/v1/im/me` and saves it in the OS credential
store, the caller retries the original `exec`. The original operation is not
held open or automatically executed after token setup.

## `authenticate`

`authenticate` takes no arguments. It opens the private xHR token dialog in a
separate process; the user pastes a token generated in xHR Platform, the CLI
validates it through `/v1/im/me`, and the credential is stored in the OS
credential store — the token never passes through the model or the tool
result.

Outcomes:

```json
{"status": "authenticated", "account": "…", "company_id": "…", "employee_id": "…"}
```

```json
{"status": "cancelled"}
```

When no graphical display is available (for example over SSH), the tool
returns `AUTH_DIALOG_UNAVAILABLE` with the exact `auth token` command for the
running binary in `auth.cli_command`, so the agent can direct the user to the
hidden-prompt terminal flow instead.

Callers should request explicit user confirmation before invoking
`authenticate` (it opens a window on the user's desktop), call it with no
arguments, and retry the original `exec` once after success.

## Error envelope

Errors should remain structured and stable:

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_EXEC_TARGET",
    "message": "The requested script is not declared by the selected leaf.",
    "retryable": false
  }
}
```
