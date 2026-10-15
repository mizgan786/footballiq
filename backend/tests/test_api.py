import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_list_players_returns_results():
    resp = client.get("/api/players?limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 5
    assert "market_value_in_eur" in data[0]


def test_list_players_filter_by_name():
    resp = client.get("/api/players?name=Haaland")
    assert resp.status_code == 200
    data = resp.json()
    assert any("Haaland" in p["name"] for p in data)


def test_get_player_not_found():
    resp = client.get("/api/players/999999999")
    assert resp.status_code == 404


def test_get_player_detail_has_seasons():
    # find a real player id first
    search = client.get("/api/players?name=Saka&limit=1").json()
    assert len(search) == 1
    player_id = search[0]["id"]

    resp = client.get(f"/api/players/{player_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Bukayo Saka"
    assert len(data["seasons"]) > 0


def test_predict_valid_payload():
    payload = {
        "age": 23, "sub_position": "Right Winger", "foot": "left", "league": "GB1",
        "appearances": 35, "minutes_played": 3000, "goals": 12, "assists": 10,
        "yellow_cards": 3, "red_cards": 0,
    }
    resp = client.post("/api/predict", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["predicted_value_eur"] > 0
    assert data["model_used"]
    assert "disclaimer" in data


@pytest.mark.parametrize("bad_field,bad_value", [
    ("age", 5),               # below allowed minimum (14)
    ("foot", "sideways"),     # not in left/right/both
    ("league", "XX9"),        # not a top-5 league code
    ("appearances", -1),      # negative
])
def test_predict_rejects_invalid_input(bad_field, bad_value):
    payload = {
        "age": 23, "sub_position": "Right Winger", "foot": "left", "league": "GB1",
        "appearances": 35, "minutes_played": 3000, "goals": 12, "assists": 10,
        "yellow_cards": 3, "red_cards": 0,
    }
    payload[bad_field] = bad_value
    resp = client.post("/api/predict", json=payload)
    assert resp.status_code == 422


def test_predict_missing_required_field():
    resp = client.post("/api/predict", json={"age": 23})
    assert resp.status_code == 422


def test_compare_players():
    saka = client.get("/api/players?name=Saka&limit=1").json()[0]["id"]
    foden = client.get("/api/players?name=Foden&limit=1").json()[0]["id"]
    resp = client.post("/api/compare", json={"player_id_a": saka, "player_id_b": foden})
    assert resp.status_code == 200
    data = resp.json()
    assert data["player_a"]["name"] == "Bukayo Saka"
    assert data["player_b"]["name"] == "Phil Foden"


def test_compare_unknown_player_returns_404():
    resp = client.post("/api/compare", json={"player_id_a": 999999999, "player_id_b": 1})
    assert resp.status_code == 404


def test_model_metrics():
    resp = client.get("/api/model/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert data["model_name"]
    assert "R2" in data["test"]


def test_analytics_summary():
    resp = client.get("/api/analytics/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["players_analyzed"] > 0
    assert data["highest_valued_player"]["name"]


def test_chat_returns_503_without_api_key():
    # no OPENAI_API_KEY set in the test environment - should fail gracefully,
    # not crash. This is the real behavior a fresh clone will see until the
    # developer adds their key to backend/.env.
    resp = client.post("/api/chat", json={"message": "hello"})
    assert resp.status_code == 503


def test_chat_returns_502_on_llm_request_failure(monkeypatch):
    # a key that's present but invalid/unreachable should surface as a clean
    # 502 with a helpful detail message, not a bare 500 stack trace
    from app.services import chat_service, llm_service

    def raise_request_error(*args, **kwargs):
        raise llm_service.LLMRequestError("simulated network failure")

    monkeypatch.setattr(chat_service, "run_chat", raise_request_error)
    resp = client.post("/api/chat", json={"message": "hello"})
    assert resp.status_code == 502
    assert "simulated network failure" in resp.json()["detail"]
