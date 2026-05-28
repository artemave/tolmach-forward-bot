import pytest

from bot.config import Settings, get_settings


def test_get_settings_reads_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token-123")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "key-abc")
    monkeypatch.delenv("DEEPSEEK_MODEL", raising=False)
    monkeypatch.delenv("DEEPSEEK_BASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_PATH", raising=False)

    settings = get_settings()

    assert settings.telegram_bot_token == "token-123"
    assert settings.deepseek_api_key == "key-abc"
    assert settings.deepseek_model == "deepseek-chat"
    assert settings.deepseek_base_url == "https://api.deepseek.com"
    assert settings.database_path == "tolmach.db"


def test_environment_overrides_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "t")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "k")
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-reasoner")
    monkeypatch.setenv("DATABASE_PATH", "custom.db")

    settings = Settings()

    assert settings.deepseek_model == "deepseek-reasoner"
    assert settings.database_path == "custom.db"
