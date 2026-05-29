"""Prompt templates for the LLM calls.

Kept in one module so the wording can be iterated on without touching call logic.
"""

TRANSLATION_PROMPT = """Translate the following text into {target_language} at CEFR level {level}.
Use vocabulary and sentence structures appropriate to that level: simplify complex clauses,
swap rare words for common ones at lower levels, preserve nuance and idiom at higher levels.
Output only the translation as plain prose - no preamble, no Markdown, no quotes around it.

Text:
{text}"""


# System message used by /explain and /grammar to pin the answer language.
# We rely on a dedicated system channel (much higher compliance than mid-prompt
# directives) and avoid seeding any English category names that the model
# might mirror as headers in its response.
LANGUAGE_SYSTEM_PROMPT = """You are a teacher who only ever writes in {target_language}.
You MUST respond entirely in {target_language}. Every word of your reply, every example, and \
every technical or grammatical term, must be in {target_language}.
If you would normally use a term from another language (such as grammatical category names), \
use the natural {target_language} equivalent instead.
Calibrate vocabulary and sentence complexity to CEFR level {level}.
If you want to emphasise a word, wrap it in Telegram HTML tags: <b>bold</b> or <i>italic</i>. \
Do NOT use Markdown (no asterisks, no underscores, no leading dashes for lists, no headers). \
Any literal < > & characters in your reply must be written as &lt; &gt; &amp;."""


EXPLAIN_PROMPT = """Explain the meaning of the text below.
For a single word: the main sense, register, and one short example sentence.
For a phrase or idiom: what it means literally and how it is typically used.
Output only the explanation - no preamble, no quotes around it.
Use the Telegram HTML tags <b>...</b> and <i>...</i> sparingly for emphasis; never Markdown.

Write your reply only in {target_language}, at CEFR level {level}.

Text:
{text}"""


# Deliberately avoids the words "grammar"/"grammatical". The training-data prior
# attached to those English terms is strong enough to drag the answer into
# English even with the language directive in place. "Walk through how it is
# put together" describes the same task without the English-academic anchor.
GRAMMAR_PROMPT = """The user wants to understand how the {target_language} text below is \
put together.
Walk them through it: what each word is doing, why it takes the form it does, and anything \
interesting about how the words fit together.
Output only your walkthrough - no preamble, no quotes around it.
Use the Telegram HTML tags <b>...</b> and <i>...</i> sparingly for emphasis; never Markdown.

Write your reply only in {target_language}, at CEFR level {level}.

Text:
{text}"""


def build_translation_prompt(*, target_language: str, level: str, text: str) -> str:
    """Render the translation prompt for a target language, CEFR level, and source text."""
    return TRANSLATION_PROMPT.format(
        target_language=target_language,
        level=level,
        text=text,
    )


def build_language_system_message(*, target_language: str, level: str) -> str:
    """Render the system message that pins the answer language for /explain and /grammar."""
    return LANGUAGE_SYSTEM_PROMPT.format(target_language=target_language, level=level)


def build_explain_prompt(*, target_language: str, level: str, text: str) -> str:
    """Render the /explain user prompt for a target language, CEFR level, and source text."""
    return EXPLAIN_PROMPT.format(
        target_language=target_language,
        level=level,
        text=text,
    )


def build_grammar_prompt(*, target_language: str, level: str, text: str) -> str:
    """Render the /grammar user prompt for a target language, CEFR level, and source text."""
    return GRAMMAR_PROMPT.format(
        target_language=target_language,
        level=level,
        text=text,
    )
