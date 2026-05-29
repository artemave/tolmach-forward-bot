"""Prompt templates for the LLM calls.

Kept in one module so the wording can be iterated on without touching call logic.
"""

TRANSLATION_PROMPT = """Translate the following text into {target_language} at CEFR level {level}.
Use vocabulary and sentence structures appropriate to that level: simplify complex clauses,
swap rare words for common ones at lower levels, preserve nuance and idiom at higher levels.
Output only the translation - no preamble, no explanation, no quotes around it.

Text:
{text}"""


# System message used by /explain and /grammar to pin the answer language.
# The LLM has strong English priors for "explain X" tasks, so the language
# instruction goes into a dedicated system channel rather than buried in
# the user prompt - and explicitly forbids switching languages even for
# technical or grammatical terms (the specific failure mode we hit).
LANGUAGE_SYSTEM_PROMPT = """You are a {target_language} tutor.
Every word of your reply must be in {target_language}, using vocabulary appropriate for CEFR \
level {level}.
Never switch to any other language - not even for technical or grammatical terms. Use the \
natural equivalents in {target_language} instead."""


EXPLAIN_PROMPT = """Explain the meaning of the text below in {target_language}, suitable for a \
CEFR {level} learner.
For a single word: the main sense, register, and one short example sentence.
For a phrase or idiom: what it means literally and how it is typically used.
Output only the explanation - no preamble, no quotes around it.

Text:
{text}"""


GRAMMAR_PROMPT = """Explain the grammar of the text below in {target_language}, suitable for a \
CEFR {level} learner.
Cover whatever is most relevant - tense, agreement, word order, notable constructions - using \
the natural grammatical vocabulary of {target_language}.
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
