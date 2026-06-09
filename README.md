# Tolmach F

A Telegram bot ([`@tolmach_forward_bot`](https://t.me/tolmach_forward_bot)) that translates
any forwarded post or typed message into your chosen language at your chosen CEFR level
(A1–C2). Configure your target language and level once with `/language` and `/level`, then
just forward and read.

## Quick start

Requires [`uv`](https://docs.astral.sh/uv/). Everything runs through `uv`.

```sh
uv sync                 # create the venv and install deps from uv.lock
cp .env.example .env    # then fill in TELEGRAM_BOT_TOKEN and OPENAI_API_KEY
uv run tolmach          # start long-polling
```

## Configuration

All configuration is via environment variables (a local `.env` is loaded automatically):

| Variable           | Required | Default                     | Purpose                                   |
| ------------------ | -------- | --------------------------- | ----------------------------------------- |
| `TELEGRAM_BOT_TOKEN`| yes      | —                            | Telegram Bot API token from @BotFather    |
| `OPENAI_API_KEY`    | yes      | —                            | OpenAI API key                            |
| `OPENAI_MODEL`      | no       | `gpt-4o-mini`                | Model name passed to the OpenAI SDK       |
| `OPENAI_BASE_URL`   | no       | `https://api.openai.com/v1`  | Override to point at another endpoint     |
| `DATABASE_PATH`     | no       | `tolmach.db`                 | Path to the SQLite database file          |

## Bot commands

| Command     | Description                                                  |
| ----------- | ------------------------------------------------------------ |
| `/start`    | Set up your language and level                               |
| `/language` | Change target language                                       |
| `/level`    | Change CEFR level (A1–C2)                                    |
| `/settings` | Show current configuration                                   |
| `/explain`  | Quote-reply with a word/phrase to get its meaning explained  |
| `/grammar`  | Quote-reply with a phrase to get a grammar breakdown         |
| `/help`     | How to use Tolmach                                           |

Anything else you send — plain text, a forwarded post, or media with a caption — comes back
translated. Media without text gets a polite no-op.

**Quote-reply commands**: long-press a message, tap *Reply*, drag the handles to select just
the part you want, then send `/explain` or `/grammar`. Tolmach answers in your configured
language at your configured CEFR level — same settings as for translations.

## Development

A `Makefile` exposes the canonical workflow. Bare `make` runs `check` (what CI runs) —
it must be green. `make help` prints the full menu of targets.

```sh
make          # = make check (lint + type + test; the default)
make lint     # ruff check + ruff format --check
make type     # mypy --strict bot tests
make test     # pytest with 100% line+branch coverage
make fix      # ruff check --fix + ruff format
make audit    # pip-audit against the lockfile
```

### Non-negotiable quality bars

- **100% coverage**, line *and* branch. No `# pragma: no cover` in `bot/`.
- **Ruff** with the `ALL` ruleset; every ignore is documented in `pyproject.toml`.
- **mypy `--strict`** over `bot` and `tests`.
- **No live network in tests** — the OpenAI client is faked and SQLite runs in-memory.

## Deployment

Tolmach deploys with [Kamal](https://kamal-deploy.org/). It is a single
long-polling worker — no HTTP, no `web` role, no kamal-proxy.

What ships with the repo:

| File                  | Purpose                                                   |
| --------------------- | --------------------------------------------------------- |
| `Dockerfile`          | Multi-stage production image, non-root, runs `tolmach`    |
| `.dockerignore`       | Keeps the build context small                             |
| `config/deploy.yml`   | Kamal service / server / registry / env / volume config   |
| `.kamal/secrets`      | Env-var passthrough template (no real secrets committed)  |

### First-time setup

1. **Fill in the placeholders** in `config/deploy.yml`:
   - `image:` — your container image (e.g. `ghcr.io/youruser/tolmach`).
   - `servers.bot.hosts:` — the host you're deploying to.
   - `registry.server` / `registry.username` — your container registry.
2. **Export the secrets** in your shell (or use direnv / a vault):
   ```sh
   export KAMAL_REGISTRY_PASSWORD=...   # registry token (e.g. GHCR PAT)
   export TELEGRAM_BOT_TOKEN=...                 # @tolmach_forward_bot Bot API token
   export OPENAI_API_KEY=...            # OpenAI API key
   ```
3. **Provision the host** (installs Docker, pulls the proxy/accessory images,
   logs in to the registry):
   ```sh
   make deploy-setup    # = kamal setup
   ```

### Deploying

```sh
make deploy         # = kamal deploy   (build, push, roll out)
make deploy-logs    # = kamal app logs -f
make docker-build   # build the image locally without deploying
```

The SQLite database is mounted at `/data/tolmach.db` inside the container,
backed by the Docker named volume `tolmach-data` declared in
`config/deploy.yml`, so it persists across container replacements.
