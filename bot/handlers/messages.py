"""Free-form message handler: translate text, captions, and forwarded posts."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from telegram.constants import ChatAction

from bot.handlers import (
    NOT_CONFIGURED,
    consume_awaiting_language,
    get_db,
    get_translator,
)
from bot.handlers.commands import LANGUAGE_SET_TEMPLATE
from bot.keyboards import level_keyboard
from bot.text_extraction import extract_text

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

NOTHING_TO_TRANSLATE = "Nothing to translate in this message."


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Translate the message, or handle a pending free-text language, or no-op politely."""
    message = update.effective_message
    user = update.effective_user
    if message is None:
        return
    if user is None:
        return

    text = extract_text(message)
    if text is None:
        await message.reply_text(NOTHING_TO_TRANSLATE)
        return

    database = get_db(context)

    if consume_awaiting_language(context):
        await database.set_language(user.id, text)
        logger.info("language set via free-text: user=%s lang=%s", user.id, text)
        await message.reply_text(
            LANGUAGE_SET_TEMPLATE.format(language=text),
            reply_markup=level_keyboard(),
        )
        return

    stored = await database.get_user(user.id)
    # Check the fields explicitly (rather than ``is_configured``) so the type checker can
    # narrow them to ``str`` for the translate call below.
    if stored is None or stored.target_language is None or stored.level is None:
        await message.reply_text(NOT_CONFIGURED)
        return

    translator = get_translator(context)
    await context.bot.send_chat_action(chat_id=message.chat_id, action=ChatAction.TYPING)
    translation = await translator.translate(
        text=text,
        target_language=stored.target_language,
        level=stored.level,
    )
    await database.save_last_post(user.id, text, translation)
    await message.reply_text(translation)
    logger.info(
        "translated user=%s lang=%s level=%s in_chars=%d out_chars=%d",
        user.id,
        stored.target_language,
        stored.level,
        len(text),
        len(translation),
    )
