"""Prompt templates for the LLM calls.

Kept in one module so the wording can be iterated on without touching call logic.
"""

TRANSLATION_PROMPT = """Translate the following text into {target_language} at CEFR level {level}.
Use vocabulary and sentence structures appropriate to that level: simplify complex clauses,
swap rare words for common ones at lower levels, preserve nuance and idiom at higher levels.
Output only the translation - no preamble, no explanation, no quotes around it.

Text:
{text}"""


EXPLAIN_PROMPT = """Write your entire reply in {target_language} at CEFR level {level}.
Do not use English in the reply unless the target language is English.

Explain the meaning of the text shown below.
For a single word, cover the main sense, register, and one short example of use.
For a phrase or idiom, cover what it means literally and how it is typically used.
Output only the explanation - no preamble, no quotes around it.

Text:
{text}"""


GRAMMAR_PROMPT = """Write your entire reply in {target_language} at CEFR level {level}.
Do not use English in the reply unless the target language is English.

Explain the grammar of the text shown below. Cover tense, mood, voice, agreement, word order,
and any notable constructions. Be concise.
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


def build_explain_prompt(*, target_language: str, level: str, text: str) -> str:
    """Render the /explain prompt for a target language, CEFR level, and source text."""
    return EXPLAIN_PROMPT.format(
        target_language=target_language,
        level=level,
        text=text,
    )


def build_grammar_prompt(*, target_language: str, level: str, text: str) -> str:
    """Render the /grammar prompt for a target language, CEFR level, and source text."""
    return GRAMMAR_PROMPT.format(
        target_language=target_language,
        level=level,
        text=text,
    )
