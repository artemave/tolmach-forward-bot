"""Shared fixtures and factories: in-memory DB, a fake DeepSeek client, and Update builders."""

from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING, cast
from unittest.mock import AsyncMock, MagicMock

import pytest_asyncio
from openai import AsyncOpenAI
from telegram import CallbackQuery, Message, TextQuote, Update, User
from telegram.ext import CallbackContext, ContextTypes

from bot.db import Database
from bot.handlers import BOT_DATA_DB, BOT_DATA_TRANSLATOR
from bot.translator import Translator

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


# --------------------------------------------------------------------------- #
# Fake DeepSeek (OpenAI-compatible) client
# --------------------------------------------------------------------------- #
class FakeCompletions:
    """Records calls and returns a canned chat completion shaped like the real SDK."""

    def __init__(self, content: str | None) -> None:
        self._content = content
        self.calls: list[dict[str, object]] = []

    async def create(self, *, model: str, messages: object) -> SimpleNamespace:
        self.calls.append({"model": model, "messages": messages})
        message = SimpleNamespace(content=self._content)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class FakeOpenAIClient:
    """Stand-in for ``AsyncOpenAI`` exposing only ``chat.completions.create``."""

    def __init__(self, content: str | None = "TRANSLATED") -> None:
        self.completions = FakeCompletions(content)
        self.chat = SimpleNamespace(completions=self.completions)


def make_translator(*, content: str | None = "TRANSLATED") -> Translator:
    """Build a real :class:`Translator` backed by the fake client."""
    client = FakeOpenAIClient(content)
    return Translator(client=cast(AsyncOpenAI, client), model="fake-model")


# --------------------------------------------------------------------------- #
# Telegram object factories (mocks cast to the real types at the boundary)
# --------------------------------------------------------------------------- #
def make_user(user_id: int = 1) -> User:
    return User(id=user_id, is_bot=False, first_name="Tester")


def make_message(
    *,
    text: str | None = None,
    caption: str | None = None,
    reply_to: Message | None = None,
    quote_text: str | None = None,
) -> Message:
    message = AsyncMock(spec=Message)
    message.text = text
    message.caption = caption
    message.reply_to_message = reply_to
    if quote_text is None:
        message.quote = None
    else:
        quote = MagicMock(spec=TextQuote)
        quote.text = quote_text
        message.quote = quote
    return cast("Message", message)


def make_callback_query(*, data: str | None, user: User | None = None) -> CallbackQuery:
    query = AsyncMock(spec=CallbackQuery)
    query.data = data
    query.from_user = make_user() if user is None else user
    return cast("CallbackQuery", query)


def make_update(
    *,
    message: Message | None = None,
    user: User | None = None,
    callback_query: CallbackQuery | None = None,
) -> Update:
    update = MagicMock(spec=Update)
    update.effective_message = message
    update.effective_user = user
    update.callback_query = callback_query
    return cast("Update", update)


def make_context(
    *,
    database: Database | None = None,
    translator: Translator | None = None,
    user_data: dict[str, object] | None = None,
    error: Exception | None = None,
) -> ContextTypes.DEFAULT_TYPE:
    context = MagicMock(spec=CallbackContext)
    bot_data: dict[str, object] = {}
    if database is not None:
        bot_data[BOT_DATA_DB] = database
    if translator is not None:
        bot_data[BOT_DATA_TRANSLATOR] = translator
    context.bot_data = bot_data
    context.user_data = user_data
    context.error = error
    return cast("ContextTypes.DEFAULT_TYPE", context)


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #
@pytest_asyncio.fixture
async def database() -> AsyncIterator[Database]:
    db = await Database.connect(":memory:")
    try:
        yield db
    finally:
        await db.close()
