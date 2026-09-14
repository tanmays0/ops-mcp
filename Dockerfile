# OpsMCP stdio server image (remote/demo). For local Cursor, prefer `uv run`.
FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
COPY src ./src
COPY fixtures ./fixtures
COPY README.md ./

RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Secrets (OPS_MCP_GITHUB_TOKEN, OPS_MCP_DATABASE_URL, OPS_MCP_FS_ROOTS) via runtime env.
CMD ["uv", "run", "python", "-m", "ops_mcp"]
