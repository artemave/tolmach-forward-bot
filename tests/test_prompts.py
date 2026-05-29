from bot.prompts import (
    TRANSLATION_PROMPT,
    build_explain_prompt,
    build_grammar_prompt,
    build_language_system_message,
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
# /explain and /grammar prompts
# --------------------------------------------------------------------------- #
def test_build_explain_prompt_includes_all_inputs() -> None:
    result = build_explain_prompt(target_language="Spanish", level="B1", text="misanthrope")
    assert "Spanish" in result
    assert "B1" in result
    assert "misanthrope" in result


def test_build_grammar_prompt_includes_all_inputs() -> None:
    result = build_grammar_prompt(target_language="French", level="B2", text="parce que tu es")
    assert "French" in result
    assert "B2" in result
    assert "parce que tu es" in result


def test_build_language_system_message_pins_target_language_and_level() -> None:
    result = build_language_system_message(target_language="Russian", level="B1")
    assert "Russian" in result
    assert "B1" in result
    # Should not single out English (bot users aren't all English speakers).
    assert "English" not in result
