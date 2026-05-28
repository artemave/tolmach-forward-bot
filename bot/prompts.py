"""Prompt templates for the translation call.

Kept in one module so the wording can be iterated on without touching call logic.
"""

TRANSLATION_PROMPT = """Translate the following text into {target_language} at CEFR level {level}.
Use vocabulary and sentence structures appropriate to that level: simplify complex clauses,
swap rare words for common ones at lower levels, preserve nuance and idiom at higher levels.
Output only the translation - no preamble, no explanation, no quotes around it.

Text:
{text}"""


def build_translation_prompt(*, target_language: str, level: str, text: str) -> str:
    """Render the translation prompt for a target language, CEFR level, and source text."""
    return TRANSLATION_PROMPT.format(
        target_language=target_language,
        level=level,
        text=text,
    )
