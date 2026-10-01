# Agent Scripts Clean DI Structure

## Dependency flow (clean DI)
- `core` defines models and interfaces (ports).
- `infrastructure` provides implementations and environment wiring.
- Tool entrypoints (outside `src`) are the composition root.
- `shared` hosts cross-cutting helpers used by multiple use-cases.

Key rule: `core` should not import from `infrastructure`.

## Folder map
- Tool folders (outside `src/`): `SKILL.md` entrypoints define the skill tree, and `<tool>.py` wrappers expose the executable runtime surface.
- `src/config/`: configuration (`app_config.py`).
- `src/core/`
  - `interfaces/`: ports (e.g. HTTP client interface).
  - `models/`: core types (e.g. request context).
- `src/infrastructure/`
  - `di/`: dependency injection container.
  - `env/`: request context builder.
  - `http/`: HTTP client implementation.
- `src/application/<domain>/`: use-cases per domain, each exposes
  `run(task_args, context, http_client)`.
- `src/shared/`: shared helpers (normalize, auth, http, workbench filters).

## DI wiring
- `src/infrastructure/di/container.py` builds `AppConfig`, request context, and
  the HTTP client.
- `src/infrastructure/di/singleton_container.py` exposes a singleton `container`.
- Entrypoint scripts call the use-case with DI-provided context and client.

## Adding new dependencies
1) Define the interface in `src/core/interfaces`.
2) Implement it in `src/infrastructure`.
3) Register it in `src/infrastructure/di/container.py`.
4) Inject it into use-cases through the container.

