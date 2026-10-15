"""
Tests the tool-calling loop and RAG injection in chat_service.run_chat()
against a mocked LLM provider. This is what proves the orchestration logic
is correct without needing a real OpenAI API call, which this sandbox
can't make (network egress here doesn't reach api.openai.com). The tool
executors themselves run for real, against the real seeded test database -
only the LLM's text/tool-call decisions are faked.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database.db import SessionLocal
from app.services import chat_service, llm_service
from app.services.llm_service import LLMResponse, ToolCall


class FakeProvider:
    """Returns queued responses in order, one per .chat() call - lets a test
    script a multi-round tool-calling conversation."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def chat(self, messages, tools=None):
        self.calls.append({"messages": messages, "tools": tools})
        return self._responses.pop(0)


def _db():
    return SessionLocal()


def test_simple_reply_with_no_tool_call(monkeypatch):
    fake = FakeProvider([LLMResponse(content="Offside is when...", tool_calls=[])])
    monkeypatch.setattr(chat_service.llm_service, "get_provider", lambda: fake)

    db = _db()
    result = chat_service.run_chat(db, "Explain the offside rule")
    db.close()

    assert result["reply"] == "Offside is when..."
    # the offside question should have triggered RAG retrieval
    assert any(s["title"].lower() == "offside" for s in result["sources"])
    assert len(fake.calls) == 1


def test_tool_call_then_final_answer(monkeypatch):
    tool_call = ToolCall(id="call_1", name="search_players", arguments={"name": "Saka", "limit": 1})
    fake = FakeProvider([
        LLMResponse(content=None, tool_calls=[tool_call]),
        LLMResponse(content="Bukayo Saka plays for Arsenal FC.", tool_calls=[]),
    ])
    monkeypatch.setattr(chat_service.llm_service, "get_provider", lambda: fake)

    db = _db()
    result = chat_service.run_chat(db, "Tell me about Saka")
    db.close()

    assert result["reply"] == "Bukayo Saka plays for Arsenal FC."
    assert len(fake.calls) == 2

    # the tool result actually fed back to the model must contain real DB data
    second_call_messages = fake.calls[1]["messages"]
    tool_result_msg = next(m for m in second_call_messages if m.get("role") == "tool")
    assert "Saka" in tool_result_msg["content"]
    assert "Arsenal" in tool_result_msg["content"]


def test_get_player_detail_tool_includes_live_prediction(monkeypatch):
    tool_call = ToolCall(id="call_1", name="get_player_detail", arguments={"name": "Saka"})
    fake = FakeProvider([
        LLMResponse(content=None, tool_calls=[tool_call]),
        LLMResponse(content="Saka's actual value differs from the model estimate.", tool_calls=[]),
    ])
    monkeypatch.setattr(chat_service.llm_service, "get_provider", lambda: fake)

    db = _db()
    chat_service.run_chat(db, "Explain Saka's valuation")
    db.close()

    second_call_messages = fake.calls[1]["messages"]
    tool_result_msg = next(m for m in second_call_messages if m.get("role") == "tool")
    assert "predicted_value_eur" in tool_result_msg["content"]
    assert "statistical model estimate" in tool_result_msg["content"]


def test_undervalued_players_tool_returns_sorted_results(monkeypatch):
    tool_call = ToolCall(id="call_1", name="undervalued_players", arguments={"limit": 3})
    fake = FakeProvider([
        LLMResponse(content=None, tool_calls=[tool_call]),
        LLMResponse(content="Here are some undervalued players.", tool_calls=[]),
    ])
    monkeypatch.setattr(chat_service.llm_service, "get_provider", lambda: fake)

    db = _db()
    result = chat_service.run_chat(db, "Show me undervalued players")
    db.close()

    assert result["reply"] == "Here are some undervalued players."
    import json
    tool_result_msg = next(m for m in fake.calls[1]["messages"] if m.get("role") == "tool")
    parsed = json.loads(tool_result_msg["content"])
    assert len(parsed["results"]) == 3
    diffs = [r["difference_pct"] for r in parsed["results"]]
    assert diffs == sorted(diffs, reverse=True)


def test_max_tool_rounds_does_not_infinite_loop(monkeypatch):
    # a pathological LLM that always wants to call a tool, never answers
    tool_call = ToolCall(id="call_1", name="top_players", arguments={"limit": 1})
    fake = FakeProvider([LLMResponse(content=None, tool_calls=[tool_call]) for _ in range(10)])
    monkeypatch.setattr(chat_service.llm_service, "get_provider", lambda: fake)

    db = _db()
    result = chat_service.run_chat(db, "top players")
    db.close()

    assert len(fake.calls) == chat_service.MAX_TOOL_ROUNDS
    assert "reply" in result
