"""Inline keyboard builders for the language and level pickers."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

LANGUAGE_CALLBACK_PREFIX = "lang"
LEVEL_CALLBACK_PREFIX = "level"
OTHER_LANGUAGE = "other"

#: Languages offered as one-tap buttons; "Other" covers everything else.
COMMON_LANGUAGES: tuple[str, ...] = (
    "English",
    "Spanish",
    "French",
    "German",
    "Italian",
    "Portuguese",
    "Russian",
    "Japanese",
)

#: The six CEFR levels, beginner to advanced.
CEFR_LEVELS: tuple[str, ...] = ("A1", "A2", "B1", "B2", "C1", "C2")


def language_keyboard() -> InlineKeyboardMarkup:
    """Build the language picker: common languages plus an "Other" free-text option."""
    buttons = [
        InlineKeyboardButton(language, callback_data=f"{LANGUAGE_CALLBACK_PREFIX}:{language}")
        for language in COMMON_LANGUAGES
    ]
    rows = [buttons[index : index + 2] for index in range(0, len(buttons), 2)]
    other = InlineKeyboardButton(
        "Other language",
        callback_data=f"{LANGUAGE_CALLBACK_PREFIX}:{OTHER_LANGUAGE}",
    )
    rows.append([other])
    return InlineKeyboardMarkup(rows)


def level_keyboard() -> InlineKeyboardMarkup:
    """Build the CEFR level picker (A1-C2)."""
    buttons = [
        InlineKeyboardButton(level, callback_data=f"{LEVEL_CALLBACK_PREFIX}:{level}")
        for level in CEFR_LEVELS
    ]
    rows = [buttons[index : index + 3] for index in range(0, len(buttons), 3)]
    return InlineKeyboardMarkup(rows)
