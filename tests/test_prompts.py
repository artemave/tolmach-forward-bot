from bot.prompts import (
    TRANSLATION_PROMPT,
    build_explain_prompt,
    build_grammar_prompt,
    build_translation_prompt,
)


def test_build_translation_prompt_includes_all_inputs() -> None:
    result = build_translation_prompt(target_language="Spanish", level="B1", text="Hello world")
    assert "Spanish" in result
    assert "B1" in result
    assert "Hello world" in result


def test_build_translation_prompt_matches_template() -> None:
    result = build_translation_prompt(target_language="French", level="A2", text="Bonjour")
    assert result == TRANSLATION_PROMPT.format(
        target_language="French",
        level="A2",
        text="Bonjour",
    )


# --------------------------------------------------------------------------- #
# /explain prompts
# --------------------------------------------------------------------------- #
def test_build_explain_prompt_with_reference_uses_reference_as_language_hint() -> None:
    result = build_explain_prompt(
        target_language="Spanish",
        level="B1",
        text="misanthrope",
        reference="The article was originally in English ...",
    )
    assert "REFERENCE" in result
    assert "originally in English" in result
    assert "misanthrope" in result
    assert "B1" in result
    # When there's a reference, the target_language is not the answer language,
    # so it shouldn't be templated in.
    assert "Spanish" not in result


def test_build_explain_prompt_without_reference_falls_back_to_target_language() -> None:
    result = build_explain_prompt(
        target_language="Spanish",
        level="A2",
        text="misanthrope",
        reference=None,
    )
    assert "Spanish" in result
    assert "A2" in result
    assert "misanthrope" in result
    assert "REFERENCE" not in result


# --------------------------------------------------------------------------- #
# /grammar prompts
# --------------------------------------------------------------------------- #
def test_build_grammar_prompt_with_reference_uses_reference_as_language_hint() -> None:
    result = build_grammar_prompt(
        target_language="French",
        level="B2",
        text="parce que tu es",
        reference="J'aime le pain.",
    )
    assert "REFERENCE" in result
    assert "J'aime le pain." in result
    assert "parce que tu es" in result
    assert "B2" in result
    assert "French" not in result


def test_build_grammar_prompt_without_reference_falls_back_to_target_language() -> None:
    result = build_grammar_prompt(
        target_language="French",
        level="C1",
        text="parce que tu es",
        reference=None,
    )
    assert "French" in result
    assert "C1" in result
    assert "parce que tu es" in result
    assert "REFERENCE" not in result
