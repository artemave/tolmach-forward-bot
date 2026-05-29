"""Entry point: build the Application, wire dependencies, and start long-polling."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from bot.config import get_settings
from bot.db import Database
from bot.handlers import BOT_DATA_DB, BOT_DATA_TRANSLATOR, commands, messages
from bot.keyboards import LANGUAGE_CALLBACK_PREFIX, LEVEL_CALLBACK_PREFIX
from bot.translator import build_translator

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine
    from typing import Any

    from telegram.ext import Application, ContextTypes

    from bot.config import Settings

    # Fully-parametrised aliases keep ``Any`` out of the annotation source (Ruff ANN401)
    # while satisfying mypy's ``disallow_any_generics``. PTB itself types these as bare
    # ``Application``, which is effectively ``Application[Any, ...]``.
    DefaultApp = Application[Any, Any, Any, Any, Any, Any]
    PostInit = Callable[[DefaultApp], Coroutine[Any, Any, None]]

logger = logging.getLogger(__name__)


def _configure_logging() -> None:
    """Send INFO+ logs to stderr with timestamps so ``kamal app logs`` is useful.

    A no-op when the root logger is already configured (e.g. under pytest),
    so it doesn't fight the test runner's log capture.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    # Trim the noisy internals so INFO is signal, not chatter.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("telegram.ext.Application").setLevel(logging.WARNING)
    logging.getLogger("telegram.ext.Updater").setLevel(logging.WARNING)


def _make_post_init(settings: Settings) -> PostInit:
    """Build the post-init hook that opens the database and the translator."""

    async def post_init(application: DefaultApp) -> None:
        application.bot_data[BOT_DATA_DB] = await Database.connect(settings.database_path)
        application.bot_data[BOT_DATA_TRANSLATOR] = build_translator(settings)
        logger.info(
            "post-init complete (db=%s model=%s)", settings.database_path, settings.deepseek_model
        )

    return post_init


async def _on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log unhandled handler exceptions with whatever update context we have."""
    update_id: int | None = None
    user_id: int | None = None
    if isinstance(update, Update):
        update_id = update.update_id
        if update.effective_user is not None:
            user_id = update.effective_user.id
    logger.error(
        "unhandled exception (update=%s user=%s): %r",
        update_id,
        user_id,
        context.error,
        exc_info=context.error,
    )


def main() -> None:
    """Configure the bot from the environment and run it via long-polling."""
    _configure_logging()
    load_dotenv()
    settings = get_settings()

    application = (
        ApplicationBuilder()
        .token(settings.telegram_bot_token)
        .post_init(_make_post_init(settings))
        .build()
    )

    application.add_error_handler(_on_error)

    application.add_handler(CommandHandler("start", commands.start))
    application.add_handler(CommandHandler("language", commands.language_command))
    application.add_handler(CommandHandler("level", commands.level_command))
    application.add_handler(CommandHandler("settings", commands.settings_command))
    application.add_handler(CommandHandler("explain", commands.explain_command))
    application.add_handler(CommandHandler("grammar", commands.grammar_command))
    application.add_handler(CommandHandler("help", commands.help_command))
    application.add_handler(
        CallbackQueryHandler(commands.language_callback, pattern=f"^{LANGUAGE_CALLBACK_PREFIX}:"),
    )
    application.add_handler(
        CallbackQueryHandler(commands.level_callback, pattern=f"^{LEVEL_CALLBACK_PREFIX}:"),
    )
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, messages.handle_message))

    logger.info("starting bot (model=%s db=%s)", settings.deepseek_model, settings.database_path)
    application.run_polling()
