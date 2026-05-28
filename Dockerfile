# syntax=docker/dockerfile:1.7
# Production image for Tolmach. Two stages: `builder` installs deps with uv
# into a self-contained virtualenv; `runtime` is a minimal slim image carrying
# just that venv and running the `tolmach` console script as a non-root user.

# ---------- builder ----------
FROM python:3.14-slim AS builder

# Pull a static uv binary from Astral's official image. Pinned to match the
# dev container so the same resolver version is used end-to-end.
COPY --from=ghcr.io/astral-sh/uv:0.11.16 /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Step 1 — install just the locked dependencies. This layer stays cached as
# long as pyproject.toml / uv.lock don't change.
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable --no-install-project

# Step 2 — install the project itself (non-editable, so no source needed at
# runtime). The wheel ends up inside /app/.venv/lib/.../site-packages.
COPY bot ./bot
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# ---------- runtime ----------
FROM python:3.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    DATABASE_PATH=/data/tolmach.db

# Non-root user. /data holds the SQLite database and is the only writable
# location the bot needs.
RUN groupadd --system --gid 1000 tolmach \
 && useradd  --system --uid 1000 --gid tolmach \
        --home-dir /app --shell /usr/sbin/nologin tolmach \
 && mkdir -p /app /data \
 && chown tolmach:tolmach /app /data

# Only the venv comes across — no source, no build tooling, no uv binary.
COPY --from=builder --chown=tolmach:tolmach /app/.venv /app/.venv

USER tolmach
WORKDIR /app
VOLUME ["/data"]

# Console script installed by uv from [project.scripts] in pyproject.toml.
CMD ["tolmach"]
