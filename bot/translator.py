"""Translation, /explain, and /grammar through DeepSeek via the OpenAI async client."""

from __future__ import annotations

from typing import TYPE_CHECKING

from openai import AsyncOpenAI

from bot.prompts import (
    build_explain_prompt,
    build_grammar_prompt,
    build_translation_prompt,
)

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletionUserMessageParam

    from bot.config import Settings


class Translator:
    """Translate, explain, and grammar-break-down text via a single LLM call each."""

    def __init__(self, client: AsyncOpenAI, model: str) -> None:
        """Wrap an OpenAI-compatible async client pinned to a model name."""
        self._client = client
        self._model = model

    async def translate(self, *, text: str, target_language: str, level: str) -> str:
        """Return ``text`` translated into ``target_language`` at the given CEFR ``level``."""
        return await self._complete(
            build_translation_prompt(
                target_language=target_language,
                level=level,
                text=text,
            ),
        )

    async def explain(self, *, text: str, target_language: str, level: str) -> str:
        """Explain ``text`` in ``target_language`` at the given CEFR ``level``."""
        return await self._complete(
            build_explain_prompt(
                target_language=target_language,
                level=level,
                text=text,
            ),
        )

    async def grammar(self, *, text: str, target_language: str, level: str) -> str:
        """Break down the grammar of ``text`` in ``target_language`` at the given CEFR ``level``."""
        return await self._complete(
            build_grammar_prompt(
                target_language=target_language,
                level=level,
                text=text,
            ),
        )

    async def _complete(self, prompt: str) -> str:
        messages: list[ChatCompletionUserMessageParam] = [
            {"role": "user", "content": prompt},
        ]
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
        )
        content = response.choices[0].message.content
        if content is None:
            return ""
        return content.strip()


def build_translator(settings: Settings) -> Translator:
    """Construct a :class:`Translator` wired to DeepSeek from ``settings``."""
    client = AsyncOpenAI(
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
    )
    return Translator(client=client, model=settings.deepseek_model)
