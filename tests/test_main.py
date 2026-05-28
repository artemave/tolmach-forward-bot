import logging
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import MagicMock

import pytest

from bot.config import Settings
from bot.db import Database
from bot.handlers import BOT_DATA_DB, BOT_DATA_TRANSLATOR
from bot.main import _make_post_init, _on_error, main
from bot.translator import Translator
from tests.conftest import make_context, make_update, make_user


async def test_post_init_opens_db_and_builds_translator() -> None:
    settings = Settings(
        telegram_bot_token="t",
        deepseek_api_key="k",
        database_path=":memory:",
    )
    post_init = _make_post_init(settings)
    application = SimpleNamespace(bot_data={})

    await post_init(cast("Any", application))

    database = application.bot_data[BOT_DATA_DB]
    assert isinstance(database, Database)
    assert isinstance(application.bot_data[BOT_DATA_TRANSLATOR], Translator)
    await database.close()


def test_main_builds_application_and_starts_polling(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = Settings(
        telegram_bot_token="123456:ABCDEF",
        deepseek_api_key="k",
        database_path=":memory:",
    )
    monkeypatch.setattr("bot.main.load_dotenv", lambda: None)
    monkeypatch.setattr("bot.main.get_settings", lambda: settings)
    run_polling = MagicMock()
    monkeypatch.setattr("telegram.ext.Application.run_polling", run_polling)

    main()

    run_polling.assert_called_once()


# --------------------------------------------------------------------------- #
# _on_error — three branches for (isinstance Update) and (effective_user None)
# --------------------------------------------------------------------------- #
async def test_on_error_logs_with_user_context(caplog: pytest.LogCaptureFixture) -> None:
    update = make_update(user=make_user(42))
    context = make_context(error=ValueError("boom"))

    with caplog.at_level(logging.ERROR, logger="bot.main"):
        await _on_error(update, context)

    assert "user=42" in caplog.text
    assert "boom" in caplog.text


async def test_on_error_logs_when_update_has_no_effective_user(
    caplog: pytest.LogCaptureFixture,
) -> None:
    update = make_update(user=None)
    context = make_context(error=RuntimeError("kaput"))

    with caplog.at_level(logging.ERROR, logger="bot.main"):
        await _on_error(update, context)

    assert "user=None" in caplog.text
    assert "kaput" in caplog.text


async def test_on_error_logs_when_update_is_not_an_update(
    caplog: pytest.LogCaptureFixture,
) -> None:
    context = make_context(error=ValueError("not-an-update"))

    with caplog.at_level(logging.ERROR, logger="bot.main"):
        await _on_error(None, context)

    assert "update=None" in caplog.text
    assert "user=None" in caplog.text
