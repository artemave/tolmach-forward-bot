"""Prompt templates for the LLM calls.

Kept in one module so the wording can be iterated on without touching call logic.
"""

TRANSLATION_PROMPT = """Translate the following text into {target_language} at CEFR level {level}.
Use vocabulary and sentence structures appropriate to that level: simplify complex clauses,
swap rare words for common ones at lower levels, preserve nuance and idiom at higher levels.
Output only the translation - no preamble, no explanation, no quotes around it.

Text:
{text}"""


# /explain and /grammar reply in the language of REFERENCE (the user's last
# forwarded/typed source text) so the answer is comprehensible to them. If no
# such reference exists yet, we fall back to {target_language}.
EXPLAIN_PROMPT_WITH_REFERENCE = """Explain the meaning of TEXT in the same language as REFERENCE, \
using vocabulary appropriate for CEFR level {level}.
For a single word, cover the main sense, register, and one short example of use.
For a phrase or idiom, cover what it means literally and how it is typically used.
Output only the explanation - no preamble, no quotes around it.

REFERENCE:
{reference}

TEXT:
{text}"""

EXPLAIN_PROMPT_NO_REFERENCE = """Explain the meaning of the following text in {target_language} \
at CEFR level {level}.
For a single word, cover the main sense, register, and one short example of use.
For a phrase or idiom, cover what it means literally and how it is typically used.
Output only the explanation - no preamble, no quotes around it.

Text:
{text}"""

GRAMMAR_PROMPT_WITH_REFERENCE = """Explain the grammar of TEXT in the same language as REFERENCE, \
using vocabulary appropriate for CEFR level {level}.
Identify the tense, mood, voice, agreement, word order, and any notable constructions. Be concise.
Output only the explanation - no preamble, no quotes around it.

REFERENCE:
{reference}

TEXT:
{text}"""

GRAMMAR_PROMPT_NO_REFERENCE = """Explain the grammar of the following text in {target_language} \
at CEFR level {level}.
Identify the tense, mood, voice, agreement, word order, and any notable constructions. Be concise.
Output only the explanation - no preamble, no quotes around it.

Text:
{text}"""


def build_translation_prompt(*, target_language: str, level: str, text: str) -> str:
    """Render the translation prompt for a target language, CEFR level, and source text."""
    return TRANSLATION_PROMPT.format(
        target_language=target_language,
        level=level,
        text=text,
    )


def build_explain_prompt(
    *,
    target_language: str,
    level: str,
    text: str,
    reference: str | None,
) -> str:
    """Render the /explain prompt; the answer language is set by ``reference`` if given."""
    if reference is None:
        return EXPLAIN_PROMPT_NO_REFERENCE.format(
            target_language=target_language,
            level=level,
            text=text,
        )
    return EXPLAIN_PROMPT_WITH_REFERENCE.format(
        level=level,
        reference=reference,
        text=text,
    )


def build_grammar_prompt(
    *,
    target_language: str,
    level: str,
    text: str,
    reference: str | None,
) -> str:
    """Render the /grammar prompt; the answer language is set by ``reference`` if given."""
    if reference is None:
        return GRAMMAR_PROMPT_NO_REFERENCE.format(
            target_language=target_language,
            level=level,
            text=text,
        )
    return GRAMMAR_PROMPT_WITH_REFERENCE.format(
        level=level,
        reference=reference,
        text=text,
    )
