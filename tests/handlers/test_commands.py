from typing import cast
from unittest.mock import AsyncMock

from telegram import InlineKeyboardMarkup

from bot.db import Database
from bot.handlers import AWAITING_LANGUAGE_KEY, commands
from bot.keyboards import LANGUAGE_CALLBACK_PREFIX, LEVEL_CALLBACK_PREFIX, OTHER_LANGUAGE
from tests.conftest import (
    make_callback_query,
    make_context,
    make_message,
    make_update,
    make_user,
)


# --------------------------------------------------------------------------- #
# /start, /language, /level, /help
# --------------------------------------------------------------------------- #
async def test_start_greets_and_shows_language_keyboard() -> None:
    message = make_message(text="/start")
    update = make_update(message=message, user=make_user())

    await commands.start(update, make_context())

    reply = cast(AsyncMock, message.reply_text)
    reply.assert_called_once()
    args, kwargs = reply.call_args
    assert args[0] == commands.WELCOME
    assert isinstance(kwargs["reply_markup"], InlineKeyboardMarkup)


async def test_start_ignores_update_without_message() -> None:
    await commands.start(make_update(message=None), make_context())


async def test_language_command_shows_language_keyboard() -> None:
    message = make_message(text="/language")
    update = make_update(message=message, user=make_user())

    await commands.language_command(update, make_context())

    reply = cast(AsyncMock, message.reply_text)
    args, kwargs = reply.call_args
    assert args[0] == commands.CHOOSE_LANGUAGE
    assert isinstance(kwargs["reply_markup"], InlineKeyboardMarkup)


async def test_language_command_ignores_update_without_message() -> None:
    await commands.language_command(make_update(message=None), make_context())


async def test_level_command_shows_level_keyboard() -> None:
    message = make_message(text="/level")
    update = make_update(message=message, user=make_user())

    await commands.level_command(update, make_context())

    reply = cast(AsyncMock, message.reply_text)
    args, kwargs = reply.call_args
    assert args[0] == commands.CHOOSE_LEVEL
    assert isinstance(kwargs["reply_markup"], InlineKeyboardMarkup)


async def test_level_command_ignores_update_without_message() -> None:
    await commands.level_command(make_update(message=None), make_context())


async def test_help_command_replies_with_help_text() -> None:
    message = make_message(text="/help")
    update = make_update(message=message, user=make_user())

    await commands.help_command(update, make_context())

    cast(AsyncMock, message.reply_text).assert_called_once_with(commands.HELP_TEXT)


async def test_help_command_ignores_update_without_message() -> None:
    await commands.help_command(make_update(message=None), make_context())


# --------------------------------------------------------------------------- #
# /settings
# --------------------------------------------------------------------------- #
async def test_settings_shows_configuration(database: Database) -> None:
    await database.set_language(1, "Spanish")
    await database.set_level(1, "B1")
    message = make_message(text="/settings")
    update = make_update(message=message, user=make_user())

    await commands.settings_command(update, make_context(database=database))

    args, _ = cast(AsyncMock, message.reply_text).call_args
    assert "Spanish" in args[0]
    assert "B1" in args[0]


async def test_settings_prompts_setup_without_row(database: Database) -> None:
    message = make_message(text="/settings")
    update = make_update(message=message, user=make_user())

    await commands.settings_command(update, make_context(database=database))

    cast(AsyncMock, message.reply_text).assert_called_once_with(commands.SETTINGS_UNCONFIGURED)


async def test_settings_prompts_setup_when_only_language_set(database: Database) -> None:
    await database.set_language(1, "Spanish")
    message = make_message(text="/settings")
    update = make_update(message=message, user=make_user())

    await commands.settings_command(update, make_context(database=database))

    cast(AsyncMock, message.reply_text).assert_called_once_with(commands.SETTINGS_UNCONFIGURED)


async def test_settings_ignores_update_without_message() -> None:
    await commands.settings_command(make_update(message=None, user=make_user()), make_context())


async def test_settings_ignores_update_without_user() -> None:
    message = make_message(text="/settings")
    update = make_update(message=message, user=None)

    await commands.settings_command(update, make_context())

    cast(AsyncMock, message.reply_text).assert_not_called()


# --------------------------------------------------------------------------- #
# Language picker callback
# --------------------------------------------------------------------------- #
async def test_language_callback_sets_language_and_shows_levels(database: Database) -> None:
    query = make_callback_query(data=f"{LANGUAGE_CALLBACK_PREFIX}:Spanish")
    update = make_update(callback_query=query)

    await commands.language_callback(update, make_context(database=database, user_data={}))

    stored = await database.get_user(1)
    assert stored is not None
    assert stored.target_language == "Spanish"
    cast(AsyncMock, query.answer).assert_awaited_once()
    edit_args, edit_kwargs = cast(AsyncMock, query.edit_message_text).call_args
    assert "Spanish" in edit_args[0]
    assert isinstance(edit_kwargs["reply_markup"], InlineKeyboardMarkup)


async def test_language_callback_other_sets_awaiting_flag() -> None:
    query = make_callback_query(data=f"{LANGUAGE_CALLBACK_PREFIX}:{OTHER_LANGUAGE}")
    update = make_update(callback_query=query)
    user_data: dict[str, object] = {}

    await commands.language_callback(update, make_context(user_data=user_data))

    assert user_data[AWAITING_LANGUAGE_KEY] is True
    cast(AsyncMock, query.edit_message_text).assert_called_once_with(commands.ASK_LANGUAGE_NAME)


async def test_language_callback_other_without_user_data() -> None:
    query = make_callback_query(data=f"{LANGUAGE_CALLBACK_PREFIX}:{OTHER_LANGUAGE}")
    update = make_update(callback_query=query)

    await commands.language_callback(update, make_context(user_data=None))

    cast(AsyncMock, query.edit_message_text).assert_called_once_with(commands.ASK_LANGUAGE_NAME)


async def test_language_callback_ignores_missing_query() -> None:
    await commands.language_callback(make_update(callback_query=None), make_context())


async def test_language_callback_ignores_missing_data() -> None:
    query = make_callback_query(data=None)
    update = make_update(callback_query=query)

    await commands.language_callback(update, make_context())

    cast(AsyncMock, query.answer).assert_awaited_once()
    cast(AsyncMock, query.edit_message_text).assert_not_called()


# --------------------------------------------------------------------------- #
# Level picker callback
# --------------------------------------------------------------------------- #
async def test_level_callback_sets_level(database: Database) -> None:
    query = make_callback_query(data=f"{LEVEL_CALLBACK_PREFIX}:B1")
    update = make_update(callback_query=query)

    await commands.level_callback(update, make_context(database=database))

    stored = await database.get_user(1)
    assert stored is not None
    assert stored.level == "B1"
    cast(AsyncMock, query.edit_message_text).assert_called_once_with(
        commands.LEVEL_SET_TEMPLATE.format(level="B1"),
    )


async def test_level_callback_ignores_missing_query() -> None:
    await commands.level_callback(make_update(callback_query=None), make_context())


async def test_level_callback_ignores_missing_data() -> None:
    query = make_callback_query(data=None)
    update = make_update(callback_query=query)

    await commands.level_callback(update, make_context())

    cast(AsyncMock, query.edit_message_text).assert_not_called()
