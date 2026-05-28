"""Telegram update handlers, plus the small shared glue they all rely on.

Dependencies (the database and translator) are stashed in ``Application.bot_data`` at
startup and pulled back out here with the right types. The "awaiting a free-text
language" flag lives in per-user ``user_data``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from telegram.ext import ContextTypes

    from bot.db import Database
    from bot.translator import Translator

#: ``bot_data`` keys for the shared dependencies.
BOT_DATA_DB = "db"
BOT_DATA_TRANSLATOR = "translator"

#: ``user_data`` key set while we wait for a free-text language name after "Other".
AWAITING_LANGUAGE_KEY = "awaiting_language"


def get_db(context: ContextTypes.DEFAULT_TYPE) -> Database:
    """Return the :class:`~bot.db.Database` stored on the application."""
    return cast("Database", context.bot_data[BOT_DATA_DB])


def get_translator(context: ContextTypes.DEFAULT_TYPE) -> Translator:
    """Return the :class:`~bot.translator.Translator` stored on the application."""
    return cast("Translator", context.bot_data[BOT_DATA_TRANSLATOR])


def set_awaiting_language(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mark this user as expected to send a free-text language name next."""
    user_data = context.user_data
    if user_data is not None:
        user_data[AWAITING_LANGUAGE_KEY] = True


def consume_awaiting_language(context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Return whether we were awaiting a free-text language, clearing the flag if so."""
    user_data = context.user_data
    if user_data is None:
        return False
    if not user_data.get(AWAITING_LANGUAGE_KEY):
        return False
    del user_data[AWAITING_LANGUAGE_KEY]
    return True
