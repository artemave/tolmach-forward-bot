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


def extract_command_target(message: Message | None) -> str | None:
    """Return the text a follow-up command (``/explain``, ``/grammar``) should operate on.

    Prefers the message's quoted selection (Telegram's quote-reply UX), falling back to
    the full text/caption of the replied-to message. Returns ``None`` when neither is
    available — the caller can then nudge the user to quote-reply first.
    """
    if message is None:
        return None
    quote = message.quote
    if quote is not None and quote.text:
        return quote.text
    return extract_text(message.reply_to_message)
