# MCP Server Launch and Architecture

## Launch command

**Canonical (from repository root):**

```bash
uv sync --extra dev
uv run uvicorn backend.main:app --reload
```

- **Must run from repository root** so that both `backend` and `mcp` are importable (pyproject packages: `mcp`, `backend`). Running from `backend/` with `uvicorn main:app` will fail because `mcp` is not on the path.
- Host/port default to `0.0.0.0:8000` when using the Python entrypoint below; with `uv run uvicorn backend.main:app` pass `--host` and `--port` explicitly to override.

**Alternative (Python entrypoint, uses settings for host/port):**

```bash
uv run python -m backend.main
```

Uses [backend/main.py](backend/main.py) `if __name__ == "__main__"` and [mcp/config.py](mcp/config.py) for `mcp_server_host` and `mcp_server_port`.

**Environment:**

| Variable           | Default   | Description        |
|--------------------|-----------|--------------------|
| `MCP_SERVER_HOST`  | `0.0.0.0` | Server bind address |
| `MCP_SERVER_PORT`  | `8000`    | Server port         |

---

## Folder layout

Aligned with [.cursor/rules/mcp.mdc](.cursor/rules/mcp.mdc):

```
mcp/
  agents/      # Agent manifests (Tier A/B/C)
  langgraphs/  # LangGraph workflows and agent
  schemas/     # Pydantic tool/resource/base schemas
  tools/       # Tool implementations and registry
  resources/   # Resource implementations and registry
  middleware/  # VaultRE/Ailo clients
  storage/     # SQLite persistence
  server/      # FastAPI app factory, routes, middleware
```

---

## Transport

- **Current:** REST (FastAPI). All tool and workflow execution via HTTP JSON (`POST /v1/tools/{name}`, `POST /v1/workflows/{name}`).
- **CLI:** [mcp/cli.py](mcp/cli.py) for local execution: `run-tool`, `run-graph`, `list-tools`, `generate-token`.
- **SSE/JSON-RPC:** Documented as optional in rules; MCP transport (SSE or Streamable HTTP) can be mounted for LangChain MCP client compatibility.

---

## CLI contract

| Command | Description |
|---------|-------------|
| `python mcp/cli.py run-tool <tool_name> --input input.json` | Execute a tool with JSON input from file or stdin. |
| `python mcp/cli.py run-graph <graph_name> --input input.json` | Execute a LangGraph workflow (`weekly_vendor_report`, `arrears_detection`, `compliance_audit`). |
| `python mcp/cli.py list-tools` | List registered tool names. |
| `python mcp/cli.py generate-token --tool <tool_name>` | Generate HITL token (MVP stub). |

Workflow input JSON must include the required body field for that workflow (e.g. `property_id` or `tenancy_id`).
