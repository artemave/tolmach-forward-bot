# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

**Greenfield — not yet scaffolded.** The only source of truth is [`tolmach-spec.md`](tolmach-spec.md). No `pyproject.toml`, `bot/`, `tests/`, or `justfile` exist yet. Read the spec before doing anything; it defines the architecture, module layout, tooling, and build milestones in full. The first milestone is to scaffold the project (`uv init`, tooling config, CI) and prove the LLM pipeline end-to-end.

When the spec and this file disagree, the spec wins — update this file to match.

## What Tolmach is

A Telegram bot (`@tolmach_forward_bot`) that translates any forwarded post or typed text into the user's configured language at their configured CEFR level (A1–C2). It is a **translator, not a study tool**: text in, translation out, one LLM call per message. Extra language-learning features (phase 2) are opt-in commands acting on the user's "last post" — never auto-appended.

## Tech stack

- Python 3.12+, managed entirely with **`uv`** — `uv sync`, `uv run <cmd>`, `uv add <pkg>`. No `pip`, no manual `venv`, no `requirements.txt`. Deps live in `pyproject.toml`, pinned by `uv.lock`.
- `python-telegram-bot` v21+ (async), long-polling.
- `openai` SDK pointed at DeepSeek's base URL (`https://api.deepseek.com`); default model `deepseek-chat`.
- `aiosqlite` for storage — one table keyed by Telegram user ID.
- Config via env vars (`BOT_TOKEN`, `DEEPSEEK_API_KEY`, `DEEPSEEK_MODEL`, `DATABASE_PATH`); `python-dotenv` for local dev.

## Commands

Per the spec, a `justfile` exposes the canonical workflow (these do not exist until scaffolded):

```
just check    # lint + type + test — CI runs this and it MUST be green
just lint     # ruff check + ruff format --check
just type     # mypy --strict bot tests
just test     # pytest with coverage, fails under 100%
just fix      # ruff check --fix + ruff format
```

Run a single test: `uv run pytest tests/path/to/test_x.py::test_name`.

## Non-negotiable constraints

These are hard requirements from the spec, enforced in CI. Code that violates them is not done:

- **100% coverage, line AND branch**, enforced via `coverage.py` branch mode. The only allowed exclusions are the three in `[tool.coverage.report] exclude_also` (`if TYPE_CHECKING:`, `raise NotImplementedError`, `@overload`). **No `# pragma: no cover` anywhere in `bot/`.** Unreachable defensive code should be deleted, not excused — if a branch can't be hit, it shouldn't exist.
- **Ruff** with the `ALL` ruleset (linter + formatter); every ignore must be documented inline with why it conflicts.
- **mypy `--strict`** — no untyped defs, no implicit `Any`. Each `# type: ignore` needs a specific error code and a comment.
- **No live network in tests** — fake the DeepSeek client and use in-memory SQLite. Mock the Telegram API.

## Architecture notes

Module layout is specified in full in the spec ("Project layout"). The shape that matters:

- `bot/translator.py` + `bot/prompts.py` — the LLM call and its prompt are deliberately isolated so prompts are easy to iterate on. Keep prompt text in `prompts.py`.
- `bot/text_extraction.py` — single place that pulls translatable text out of any Telegram `Update` (message body, or media `caption`). Message-type handling rules (plain / forwarded / caption / media-without-text → polite no-op) live here and in `handlers/messages.py`.
- `bot/db.py` — per-user state: target language, CEFR level, last post (original + translation), timestamps.
- Design principle to preserve: **predictable, stateless-feeling, fail-politely.** Unsupported messages get a friendly no-op ("Nothing to translate in this message."), never an error.

## Dev environment

Runs in a devcontainer (`docker-compose.dev.yml` + `Dockerfile.dev`) built on a shared `dev-base` image, with `mise` providing `uv`. The `.venv` lives on a named Docker volume so the Linux-built virtualenv isn't shadowed by the bind-mounted host checkout — don't expect `.venv` to be usable from the host.
