from telegram import InlineKeyboardMarkup

from bot.keyboards import (
    CEFR_LEVELS,
    COMMON_LANGUAGES,
    LANGUAGE_CALLBACK_PREFIX,
    LEVEL_CALLBACK_PREFIX,
    OTHER_LANGUAGE,
    language_keyboard,
    level_keyboard,
)


def test_language_keyboard_offers_every_language_and_other() -> None:
    markup = language_keyboard()
    assert isinstance(markup, InlineKeyboardMarkup)

    buttons = [button for row in markup.inline_keyboard for button in row]
    texts = [button.text for button in buttons]
    callbacks = [button.callback_data for button in buttons]

    for language in COMMON_LANGUAGES:
        assert language in texts
        assert f"{LANGUAGE_CALLBACK_PREFIX}:{language}" in callbacks
    assert f"{LANGUAGE_CALLBACK_PREFIX}:{OTHER_LANGUAGE}" in callbacks


def test_level_keyboard_offers_every_cefr_level() -> None:
    markup = level_keyboard()
    assert isinstance(markup, InlineKeyboardMarkup)

    buttons = [button for row in markup.inline_keyboard for button in row]
    callbacks = [button.callback_data for button in buttons]

    for level in CEFR_LEVELS:
        assert f"{LEVEL_CALLBACK_PREFIX}:{level}" in callbacks
