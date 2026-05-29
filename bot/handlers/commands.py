"""Slash-command and inline-button handlers."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from bot.handlers import NOT_CONFIGURED, get_db, get_translator, set_awaiting_language
from bot.keyboards import OTHER_LANGUAGE, language_keyboard, level_keyboard
from bot.text_extraction import extract_command_target

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import ContextTypes


logger = logging.getLogger(__name__)

WELCOME = """👋 Welcome to Tolmach!

Forward me any post (or just send text) and I'll translate it into your language at your level.

First, pick the language you want translations in:"""

CHOOSE_LANGUAGE = "Pick the language you want translations in:"

CHOOSE_LEVEL = "Pick your CEFR level (A1 = beginner, C2 = advanced):"

ASK_LANGUAGE_NAME = "Type the name of the language you'd like, e.g. Dutch or Korean."

LANGUAGE_SET_TEMPLATE = "Language set to {language}. Now pick your level:"

LEVEL_SET_TEMPLATE = """Level set to {level}. You're all set! ✅

Forward me a post or send any text and I'll translate it."""

SETTINGS_TEMPLATE = """Your settings:
- Language: {language}
- Level: {level}"""

SETTINGS_UNCONFIGURED = (
    "You haven't set up Tolmach yet. Send /start to choose a language and level."
)

HELP_TEXT = """Tolmach translates anything you send into your language at your level.

How to use it:
- Forward any channel post, or just type/paste some text.
- Tolmach replies with the translation, adjusted to your CEFR level.

Want a closer look at a specific word or phrase from a translation?
Long-press the message, tap Reply, drag the handles to select just that part,
then send /explain or /grammar.

Commands:
- /start - set up your language and level
- /language - change the target language
- /level - change the CEFR level (A1-C2)
- /settings - show your current configuration
- /explain - explain a quoted word or phrase
- /grammar - break down the grammar of a quoted phrase
- /help - show this message

Media without any text gets a polite "nothing to translate" reply."""

NEEDS_QUOTE_REPLY = (
    "Quote-reply to a message first: long-press it, tap Reply, drag to select the "
    "part you want, then send /explain or /grammar again."
)


async def start(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greet the user and start onboarding with the language picker."""
    message = update.effective_message
    if message is None:
        return
    await message.reply_text(WELCOME, reply_markup=language_keyboard())


async def language_command(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the language picker."""
    message = update.effective_message
    if message is None:
        return
    await message.reply_text(CHOOSE_LANGUAGE, reply_markup=language_keyboard())


async def level_command(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the CEFR level picker."""
    message = update.effective_message
    if message is None:
        return
    await message.reply_text(CHOOSE_LEVEL, reply_markup=level_keyboard())


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the user's current language and level, or prompt them to set up."""
    message = update.effective_message
    user = update.effective_user
    if message is None:
        return
    if user is None:
        return
    stored = await get_db(context).get_user(user.id)
    if stored is None or not stored.is_configured:
        await message.reply_text(SETTINGS_UNCONFIGURED)
        return
    await message.reply_text(
        SETTINGS_TEMPLATE.format(language=stored.target_language, level=stored.level),
    )


async def help_command(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show usage help."""
    message = update.effective_message
    if message is None:
        return
    await message.reply_text(HELP_TEXT)


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle a tap on the language picker (a specific language or "Other")."""
    query = update.callback_query
    if query is None:
        return
    await query.answer()
    data = query.data
    if data is None:
        return
    _, _, value = data.partition(":")
    if value == OTHER_LANGUAGE:
        set_awaiting_language(context)
        await query.edit_message_text(ASK_LANGUAGE_NAME)
        return
    await get_db(context).set_language(query.from_user.id, value)
    logger.info("language set: user=%s lang=%s", query.from_user.id, value)
    await query.edit_message_text(
        LANGUAGE_SET_TEMPLATE.format(language=value),
        reply_markup=level_keyboard(),
    )


async def level_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle a tap on the CEFR level picker."""
    query = update.callback_query
    if query is None:
        return
    await query.answer()
    data = query.data
    if data is None:
        return
    _, _, value = data.partition(":")
    await get_db(context).set_level(query.from_user.id, value)
    logger.info("level set: user=%s level=%s", query.from_user.id, value)
    await query.edit_message_text(LEVEL_SET_TEMPLATE.format(level=value))


# --------------------------------------------------------------------------- #
# /explain and /grammar — follow-up commands operating on a quoted selection.
# --------------------------------------------------------------------------- #
async def _follow_up_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    kind: str,
) -> None:
    """Shared shape for ``/explain`` and ``/grammar``: read the quote, call the LLM, reply."""
    message = update.effective_message
    user = update.effective_user
    if message is None:
        return
    if user is None:
        return

    target = extract_command_target(message)
    if target is None:
        await message.reply_text(NEEDS_QUOTE_REPLY)
        return

    stored = await get_db(context).get_user(user.id)
    if stored is None or stored.target_language is None or stored.level is None:
        await message.reply_text(NOT_CONFIGURED)
        return

    translator = get_translator(context)
    method = translator.explain if kind == "explain" else translator.grammar
    result = await method(
        text=target,
        target_language=stored.target_language,
        level=stored.level,
    )
    await message.reply_text(result)
    logger.info(
        "%s: user=%s lang=%s level=%s chars=%d",
        kind,
        user.id,
        stored.target_language,
        stored.level,
        len(target),
    )


async def explain_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Explain the quoted (or replied-to) text in the user's reading language."""
    await _follow_up_command(update, context, kind="explain")


async def grammar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Break down the grammar of the quoted (or replied-to) text."""
    await _follow_up_command(update, context, kind="grammar")
