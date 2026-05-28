"""Pull the translatable text out of any Telegram message.

The rules for which message types carry translatable text live here so that the
message handler can stay a thin orchestration layer.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from telegram import Message


def extract_text(message: Message | None) -> str | None:
    """Return the message body or media caption, or ``None`` when there is nothing to translate.

    Plain and forwarded text messages expose their content as ``text``; photos, videos and
    documents carry it as ``caption``. Everything else (stickers, polls, media without text,
    or no message at all) yields ``None`` so the caller can reply with a polite no-op.
    """
    if message is None:
        return None
    if message.text:
        return message.text
    if message.caption:
        return message.caption
    return None
