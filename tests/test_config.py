import pytest

from bot.config import Settings, get_settings


def test_get_settings_reads_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token-123")
    monkeypatch.setenv("OPENAI_API_KEY", "key-abc")
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_PATH", raising=False)

    settings = get_settings()

    assert settings.telegram_bot_token == "token-123"
    assert settings.openai_api_key == "key-abc"
    assert settings.openai_model == "gpt-4o-mini"
    assert settings.openai_base_url == "https://api.openai.com/v1"
    assert settings.database_path == "tolmach.db"


def test_environment_overrides_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "t")
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
    monkeypatch.setenv("DATABASE_PATH", "custom.db")

    settings = Settings()

    assert settings.openai_model == "gpt-4o"
    assert settings.database_path == "custom.db"
