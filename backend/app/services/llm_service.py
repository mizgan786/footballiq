"""
llm_service.py

Abstracts the LLM provider so chat_service.py (the orchestration logic -
tool calling, RAG context injection) never touches a provider SDK
directly. Swapping providers means adding a new class here and changing
LLM_PROVIDER, not touching any calling code.

Currently implemented: OpenAI (chat.completions API, with tool/function
calling). Anthropic or others could be added the same way later.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


class LLMNotConfiguredError(Exception):
    """Raised when no API key is set for the configured provider."""


class LLMRequestError(Exception):
    """Raised when the provider is configured but the actual API call fails
    (bad key, network unreachable, rate limit, etc.) - kept distinct from
    LLMNotConfiguredError so callers can return the right status code."""


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclass
class LLMResponse:
    content: Optional[str]
    tool_calls: list = field(default_factory=list)


class OpenAIProvider:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise LLMNotConfiguredError(
                "OPENAI_API_KEY is not set. Add it to backend/.env to enable the FootballIQ Assistant."
            )
        from openai import OpenAI  # imported lazily so the app can start without the package configured

        self._client = OpenAI(api_key=api_key)
        self._model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def chat(self, messages: list, tools: Optional[list] = None) -> LLMResponse:
        import json

        kwargs = {"model": self._model, "messages": messages}
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        try:
            response = self._client.chat.completions.create(**kwargs)
        except Exception as e:
            # covers auth errors, unreachable network, rate limits, timeouts -
            # surfaced to the API layer as a clean, catchable error instead of
            # letting the raw SDK exception become an unhandled 500
            raise LLMRequestError(f"OpenAI request failed: {e}") from e

        choice = response.choices[0].message

        tool_calls = []
        for tc in getattr(choice, "tool_calls", None) or []:
            tool_calls.append(
                ToolCall(id=tc.id, name=tc.function.name, arguments=json.loads(tc.function.arguments or "{}"))
            )

        return LLMResponse(content=choice.content, tool_calls=tool_calls)


_provider_instance = None


def get_provider():
    """Lazily constructs the configured provider on first use, so importing
    this module (e.g. at app startup) never fails just because no API key
    is set yet - the error only surfaces when the chat endpoint is actually
    called."""
    global _provider_instance
    if _provider_instance is None:
        provider_name = os.getenv("LLM_PROVIDER", "openai")
        if provider_name == "openai":
            _provider_instance = OpenAIProvider()
        else:
            raise ValueError(f"Unknown LLM_PROVIDER: {provider_name}")
    return _provider_instance
