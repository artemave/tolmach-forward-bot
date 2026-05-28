# Tolmach — Project Spec

**Handle:** `@tolmach_forward_bot`

A Telegram bot that translates forwarded channel posts (and any text sent to it) into the user's chosen language at their chosen CEFR level (A1–C2). The user configures target language and level once; from then on, anything they send comes back translated and level-adjusted.

Tolmach is a **translator**, not a study tool. Core behavior is predictable: text in, translation out. Any extra language-learning features are exposed as opt-in commands operating on the most recently sent post.

## BotFather metadata

- **Name:** `Tolmach F`
- **Short description (≤120 chars):** `Forward any channel post — get it translated to your language at your level (A1–C2).`
- **About text (≤512 chars):** `Tolmach is your personal interpreter for Telegram. Forward any post (or send any text), and Tolmach translates it into your chosen language at your chosen CEFR level — from A1 beginner to C2 advanced. Configure once with /language and /level, then just forward and read. Built for language learners who want to read real, current content at the right level of difficulty.`
- **Commands:**
  ```
  start - Set up your language and level
  language - Change target language
  level - Change CEFR level (A1–C2)
  settings - Show current configuration
  help - How to use Tolmach
  ```

## Core loop

1. User sends a message to the bot (forwarded or typed).
2. Bot extracts translatable text — message body or media caption.
3. Bot translates to the user's configured target language at their configured CEFR level via an LLM.
4. Bot replies with the translation.
5. Bot stores this exchange as the user's "last post" for future follow-up commands.

## Commands

- `/start` — onboarding; prompts for target language and level via inline keyboards.
- `/language` — change target language (inline keyboard with common options + "other" for free-text input).
- `/level` — change CEFR level (A1, A2, B1, B2, C1, C2 buttons).
- `/settings` — show current configuration.
- `/help` — usage summary.

## Per-user state

Persist per Telegram user ID:
- Target language (e.g. "Spanish", "Japanese")
- CEFR level (A1–C2)
- Last post: original text + translation
- Created / updated timestamps

SQLite, one table.

## Message handling

- **Plain text** → translate the text.
- **Forwarded text message** → same; `forward_origin` metadata is optional, don't require it.
- **Media with caption** (photo, video, document) → translate the `caption` field.
- **Media without text** (image-only, sticker, voice, poll, etc.) → reply: "Nothing to translate in this message."
- **Empty or unsupported** → same polite no-op response.

## Out of scope for MVP

- Fetching and translating linked articles (phase 2 — many channels post link-only content where the meaningful text lives behind a URL).
- Vocabulary extraction, grammar explanation, side-by-side views (phase 2 — added as commands on the last post).
- Cross-user translation caching (add only if cost requires).
- Voice/audio transcription.

## LLM integration

DeepSeek API via the OpenAI-compatible SDK (`openai` Python package pointed at DeepSeek's base URL). Model configurable via env var — default to `deepseek-chat`.

Single prompt for translation + level adaptation, roughly:

> Translate the following text into {target_language} at CEFR level {level}. Use vocabulary and sentence structures appropriate to that level: simplify complex clauses, swap rare words for common ones at lower levels, preserve nuance and idiom at higher levels. Output only the translation — no preamble, no explanation, no quotes around it.
>
> Text:
> {user_text}

Keep prompts in one module so they're easy to iterate on. CEFR adherence will be approximate, not exact — acceptable for a learning tool.

One LLM call per message. Users self-throttle by only sending what they care about; no caching needed initially.

## Tech stack

- **Language:** Python 3.12+
- **Package & project manager:** `uv` (used for everything — `uv sync`, `uv run`, `uv add`; no `pip`, no `venv`, no `requirements.txt`). Pinned via `uv.lock`. Dependencies declared in `pyproject.toml`.
- **Telegram:** `python-telegram-bot` v21+ (async)
- **LLM SDK:** `openai` (configured with DeepSeek's base URL — `https://api.deepseek.com`)
- **Storage:** SQLite via `aiosqlite`
- **Config:** environment variables (`TELEGRAM_BOT_TOKEN`, `DEEPSEEK_API_KEY`, `DEEPSEEK_MODEL`, `DATABASE_PATH`); `python-dotenv` for local dev
- **Deployment:** long-polling to start; webhooks later if needed

## Development tooling

All tooling configured in `pyproject.toml` and runnable via `uv run <tool>`. Every check below must pass in CI; pre-commit hooks recommended locally.

### Linting & formatting
- **Ruff** — both linter and formatter. Enable a strict ruleset: `ALL` with targeted ignores for rules that genuinely conflict with the codebase (document each ignore with a comment). Includes pycodestyle, pyflakes, isort, pyupgrade, bugbear, comprehensions, simplify, pep8-naming, security (S), and more.
- **Ruff format** — replaces Black; one formatter, no conflicts.

### Type checking
- **mypy** in `--strict` mode. No untyped defs, no implicit `Any`, no untyped decorators, no missing return types. Third-party stubs installed where available; `# type: ignore` requires a specific error code and a comment.
- Alternative: `pyright` in strict mode is also acceptable if preferred.

### Testing
- **pytest** + **pytest-asyncio** for async handler tests.
- **pytest-cov** with **coverage.py** in branch mode.
- **Mocking:** `pytest-mock` for the Telegram API and DeepSeek client. No live network calls in tests — use fakes for the LLM and an in-memory SQLite for the DB.

### Coverage requirements

**100% coverage, no exceptions, enforced in CI.**

`pyproject.toml` coverage config:
```toml
[tool.coverage.run]
branch = true
source = ["bot"]
parallel = true

[tool.coverage.report]
fail_under = 100
show_missing = true
skip_covered = false
exclude_also = [
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
    "@overload",
]
```

Notes on the 100% bar:
- **Line coverage** must be 100%.
- **Branch coverage** must be 100% (every `if`/`elif`/`else`, every short-circuit `and`/`or`, every loop entry/skip).
- Python's `coverage.py` does not natively measure "expression coverage" or MC/DC; line + branch at 100% is the practical strictest setting and is what's enforced here.
- The only acceptable exclusions are the three in `exclude_also` above (TYPE_CHECKING blocks, explicit `NotImplementedError`, and `@overload` stubs). No `# pragma: no cover` allowed anywhere in `bot/`.
- Defensive code that can't be reached should be deleted, not excluded. If it truly can't be reached, the branch shouldn't exist.

### Security & supply chain
- **bandit** (or Ruff's `S` ruleset, which covers most of it) for security linting.
- **pip-audit** run against `uv.lock` in CI to flag known CVEs.

### One-command checks
A `Makefile` or `justfile` exposes:
```
just lint     # ruff check + ruff format --check
just type     # mypy --strict bot tests
just test     # pytest with coverage, fails under 100%
just check    # all of the above
just fix      # ruff check --fix + ruff format
```
CI runs `just check` and must pass.

## Project layout

```
bot/
  __init__.py
  main.py              # entry point, bot setup, handler registration
  config.py            # env var loading, settings (pydantic-settings or similar)
  db.py                # SQLite schema + user CRUD
  handlers/
    __init__.py
    commands.py        # /start, /language, /level, /settings, /help
    messages.py        # forwarded / plain-text / caption handling
  translator.py        # LLM call + prompt construction
  prompts.py           # prompt templates
  keyboards.py         # inline keyboard builders for language/level pickers
  text_extraction.py   # pull translatable text out of any Update
tests/
  __init__.py
  conftest.py          # shared fixtures: fake LLM, in-memory DB, Update factories
  test_config.py
  test_db.py
  test_translator.py
  test_prompts.py
  test_keyboards.py
  test_text_extraction.py
  handlers/
    test_commands.py
    test_messages.py
.env.example
pyproject.toml
uv.lock
justfile               # or Makefile
.github/workflows/ci.yml
README.md
```

## Build milestones

Every milestone ships with tests that keep coverage at 100% (line + branch) and all lint/type checks passing. No milestone is "done" until `just check` is green.

1. **End-to-end echo with hardcoded translation.** Bot receives a message, sends it to the LLM with a hardcoded language + level, replies with the result. No DB, no commands. Proves the pipeline. Also sets up the project skeleton: `uv init`, `pyproject.toml`, Ruff + mypy + pytest + coverage config, `justfile`, CI workflow.
2. **Per-user config + persistence.** Add SQLite, `/start`, `/language`, `/level`, `/settings`. Translation now uses per-user settings.
3. **Robust message-type handling.** Captions, media-without-text, edge cases. Polite fallbacks.
4. **`/help` and onboarding polish.**
5. **Track "last post" per user.** Groundwork for follow-up commands.
6. *(Phase 2)* Link extraction and article fetching for link-heavy posts.
7. *(Phase 2)* Follow-up commands: `/vocab`, `/explain`, `/grammar`.

## Design principles

- **Predictability over cleverness.** Forward = translation. No auto-appended vocab or notes.
- **Opt-in depth.** Every extra feature is a command the user explicitly invokes.
- **Stateless from the user's POV, stateful under the hood.** Future commands like `/vocab` act on the last post — no arguments, no re-forwarding.
- **Fail politely.** Unsupported message types get a friendly no-op, not an error.
