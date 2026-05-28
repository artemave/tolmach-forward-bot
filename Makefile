# Tolmach task runner. Every recipe goes through `uv` so the right venv is used.

.DEFAULT_GOAL := check

.PHONY: help check lint type test fix audit run docker-build deploy deploy-setup deploy-logs

help: ## Show this help
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check: lint type test ## Lint + type + test - what CI runs and MUST be green

lint: ## Ruff linter + formatter check (no writes)
	uv run ruff check bot tests
	uv run ruff format --check bot tests

type: ## Strict static type checking
	uv run mypy --strict bot tests

test: ## Run the test suite (coverage fails the run under 100%)
	uv run pytest

fix: ## Auto-fix lint issues and reformat
	uv run ruff check --fix bot tests
	uv run ruff format bot tests

audit: ## Flag known CVEs in the locked dependency set
	uv run pip-audit

run: ## Start the bot (long-polling). Needs BOT_TOKEN + DEEPSEEK_API_KEY in env/.env
	uv run tolmach

# --- Deployment (Kamal) ---------------------------------------------------- #
docker-build: ## Build the production image locally
	docker build -t tolmach:local .

deploy-setup: ## First-time setup on the host(s) in config/deploy.yml
	kamal setup

deploy: ## Build, push, and roll out the current commit
	kamal deploy

deploy-logs: ## Tail the bot's logs on the deployed host
	kamal app logs -f
