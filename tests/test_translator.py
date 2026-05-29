from typing import cast

from openai import AsyncOpenAI

from bot.config import Settings
from bot.translator import Translator, build_translator
from tests.conftest import FakeOpenAIClient


async def test_translate_sends_prompt_and_returns_stripped_content() -> None:
    client = FakeOpenAIClient(content="  Hola mundo  ")
    translator = Translator(client=cast("AsyncOpenAI", client), model="my-model")

    result = await translator.translate(
        text="Hello world",
        target_language="Spanish",
        level="B1",
    )

    assert result == "Hola mundo"
    assert len(client.completions.calls) == 1
    call = client.completions.calls[0]
    assert call["model"] == "my-model"
    sent = cast("list[dict[str, str]]", call["messages"])
    assert sent[0]["role"] == "user"
    assert "Spanish" in sent[0]["content"]
    assert "Hello world" in sent[0]["content"]


async def test_translate_returns_empty_string_when_content_is_none() -> None:
    client = FakeOpenAIClient(content=None)
    translator = Translator(client=cast("AsyncOpenAI", client), model="my-model")

    result = await translator.translate(text="x", target_language="French", level="A1")

    assert result == ""


# --------------------------------------------------------------------------- #
# explain / grammar
# --------------------------------------------------------------------------- #
async def test_explain_sends_language_system_message_and_returns_stripped_content() -> None:
    client = FakeOpenAIClient(content="  EXPLANATION  ")
    translator = Translator(client=cast("AsyncOpenAI", client), model="m")

    result = await translator.explain(
        text="misanthrope",
        target_language="Spanish",
        level="B1",
    )

    assert result == "EXPLANATION"
    sent = cast("list[dict[str, str]]", client.completions.calls[0]["messages"])
    assert sent[0]["role"] == "system"
    assert "Spanish" in sent[0]["content"]
    assert sent[1]["role"] == "user"
    assert "misanthrope" in sent[1]["content"]
    assert "Spanish" in sent[1]["content"]


async def test_grammar_sends_language_system_message_and_returns_stripped_content() -> None:
    client = FakeOpenAIClient(content="GRAMMAR")
    translator = Translator(client=cast("AsyncOpenAI", client), model="m")

    result = await translator.grammar(
        text="parce que tu es",
        target_language="French",
        level="C1",
    )

    assert result == "GRAMMAR"
    sent = cast("list[dict[str, str]]", client.completions.calls[0]["messages"])
    assert sent[0]["role"] == "system"
    assert "French" in sent[0]["content"]
    assert sent[1]["role"] == "user"
    assert "parce que tu es" in sent[1]["content"]


async def test_translate_does_not_send_a_system_message() -> None:
    client = FakeOpenAIClient(content="Hola")
    translator = Translator(client=cast("AsyncOpenAI", client), model="m")

    await translator.translate(text="Hello", target_language="Spanish", level="B1")

    sent = cast("list[dict[str, str]]", client.completions.calls[0]["messages"])
    assert len(sent) == 1
    assert sent[0]["role"] == "user"


def test_build_translator_wires_deepseek_settings() -> None:
    settings = Settings(
        telegram_bot_token="t",
        deepseek_api_key="secret-key",
        deepseek_model="deepseek-chat",
        deepseek_base_url="https://api.deepseek.com",
    )

    translator = build_translator(settings)

    assert isinstance(translator, Translator)
    assert translator._model == "deepseek-chat"
    assert isinstance(translator._client, AsyncOpenAI)
    assert str(translator._client.base_url).rstrip("/") == "https://api.deepseek.com"
