from bot.prompts import TRANSLATION_PROMPT, build_translation_prompt


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
