import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services import rag_service


def test_retrieve_finds_relevant_chunk_for_xg_question():
    results = rag_service.retrieve("What does xG mean?")
    assert len(results) > 0
    assert any("xg" in r["title"].lower() or "expected goals" in r["title"].lower() for r in results)


def test_retrieve_finds_offside_rule():
    results = rag_service.retrieve("Explain the offside rule in football")
    assert len(results) > 0
    assert results[0]["title"].lower() == "offside"


def test_retrieve_returns_nothing_for_unrelated_query():
    results = rag_service.retrieve("What is the capital of France?")
    assert results == []


def test_retrieve_respects_top_k():
    results = rag_service.retrieve("football league value model prediction", top_k=2)
    assert len(results) <= 2
