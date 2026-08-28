# Runtime

`runtime/agent-scripts` contains a vendored snapshot of the `agent-scripts`
runtime used by the local MCP server.

Refresh it with:

```bash
python scripts/sync_agent_scripts.py ../agent-scripts
```

The generated `runtime-version.json` records source provenance. Do not edit the
vendored copy directly.
