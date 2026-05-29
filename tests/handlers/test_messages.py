from typing import cast
from unittest.mock import AsyncMock

from telegram import InlineKeyboardMarkup

from bot.db import Database
from bot.handlers import AWAITING_LANGUAGE_KEY, NOT_CONFIGURED, messages
from tests.conftest import (
    make_context,
    make_message,
    make_translator,
    make_update,
    make_user,
)


async def test_ignores_update_without_message() -> None:
    update = make_update(message=None, user=make_user())
    await messages.handle_message(update, make_context())


async def test_ignores_update_without_user() -> None:
    message = make_message(text="Hello")
    update = make_update(message=message, user=None)

    await messages.handle_message(update, make_context())

    cast(AsyncMock, message.reply_text).assert_not_called()


async def test_polite_noop_when_nothing_to_translate() -> None:
    message = make_message(text=None, caption=None)
    update = make_update(message=message, user=make_user())

    await messages.handle_message(update, make_context())

    cast(AsyncMock, message.reply_text).assert_called_once_with(messages.NOTHING_TO_TRANSLATE)


async def test_pending_free_text_language_is_saved(database: Database) -> None:
    message = make_message(text="Dutch")
    update = make_update(message=message, user=make_user())
    context = make_context(database=database, user_data={AWAITING_LANGUAGE_KEY: True})

    await messages.handle_message(update, context)

    stored = await database.get_user(1)
    assert stored is not None
    assert stored.target_language == "Dutch"
    args, kwargs = cast(AsyncMock, message.reply_text).call_args
    assert "Dutch" in args[0]
    assert isinstance(kwargs["reply_markup"], InlineKeyboardMarkup)


async def test_prompts_setup_when_no_user_row(database: Database) -> None:
    message = make_message(text="Bonjour")
    update = make_update(message=message, user=make_user())
    context = make_context(database=database, user_data=None)

    await messages.handle_message(update, context)

    cast(AsyncMock, message.reply_text).assert_called_once_with(NOT_CONFIGURED)


async def test_prompts_setup_when_only_level_set(database: Database) -> None:
    await database.set_level(1, "B1")
    message = make_message(text="Bonjour")
    update = make_update(message=message, user=make_user())
    context = make_context(database=database, user_data={})

    await messages.handle_message(update, context)

    cast(AsyncMock, message.reply_text).assert_called_once_with(NOT_CONFIGURED)


async def test_prompts_setup_when_only_language_set(database: Database) -> None:
    await database.set_language(1, "Spanish")
    message = make_message(text="Bonjour")
    update = make_update(message=message, user=make_user())
    context = make_context(database=database, user_data={})

    await messages.handle_message(update, context)

    cast(AsyncMock, message.reply_text).assert_called_once_with(NOT_CONFIGURED)


async def test_translates_and_stores_last_post(database: Database) -> None:
    await database.set_language(1, "Spanish")
    await database.set_level(1, "B1")
    message = make_message(text="Hello world")
    update = make_update(message=message, user=make_user())
    translator = make_translator(content="Hola mundo")
    context = make_context(database=database, translator=translator, user_data={})

    await messages.handle_message(update, context)

    cast(AsyncMock, message.reply_text).assert_called_once_with("Hola mundo")
    stored = await database.get_user(1)
    assert stored is not None
    assert stored.last_original == "Hello world"
    assert stored.last_translation == "Hola mundo"
