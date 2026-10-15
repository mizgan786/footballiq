"""
chat_service.py

Orchestrates one turn of the FootballIQ Assistant:
  1. Retrieve RAG context relevant to the user's message (rag_service).
  2. Give the LLM a set of tools backed by the real player database
     (player_service / ml_service) so it can answer data questions
     ("top 5 midfielders", "explain Saka's valuation") with real numbers
     instead of guessing.
  3. Run the standard tool-calling loop: if the model requests a tool,
     execute it and feed the result back, up to a small round limit.

This keeps LLM wiring (llm_service) and data access (player_service)
both separate from this file - this module only coordinates them.
"""

import json
from sqlalchemy.orm import Session

from app.services import llm_service, rag_service, player_service, ml_service

MAX_TOOL_ROUNDS = 3

SYSTEM_PROMPT = """You are the FootballIQ Assistant, embedded in a football analytics web app.
You help users understand football rules, tactics, and analytics concepts, and answer
questions about players in the FootballIQ database (covering the Premier League, La Liga,
Bundesliga, Serie A, and Ligue 1, seasons 2012-2025) using the tools provided.

Rules:
- For questions about a specific player's stats or valuation, use the tools rather than
  guessing - the tools return real data from the database and a live model prediction.
- When you mention a "predicted" or "estimated" market value, always make clear it's a
  statistical model estimate, not an official valuation.
- If knowledge-base context is provided below, treat it as static reference material - it
  is not live or current information.
- If a player isn't found in the database, say so plainly rather than inventing stats.
- Keep answers concise and conversational, formatted in markdown where it helps
  (short lists, **bold** for key numbers) - this isn't a report, it's a chat.
"""

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search_players",
            "description": "Search for players by name (partial match ok). Returns each match's latest-season club, position, age, and market value.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "limit": {"type": "integer", "default": 5},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_player_detail",
            "description": "Get a specific player's full season history plus the model's live predicted market value and how it compares to their actual value. Use this for 'explain X's valuation' or 'why is X worth Y' questions.",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "top_players",
            "description": "Get the top N players by market value, optionally filtered by position. Use for 'top 5 midfielders', 'most valuable players', etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 5},
                    "position": {"type": "string", "enum": ["Attack", "Midfield", "Defender", "Goalkeeper"]},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "undervalued_players",
            "description": "Find players among the highest-valued in the database whose model prediction is notably above their actual market value (i.e. potentially undervalued by the market, per the model). Use for 'show me undervalued players'.",
            "parameters": {
                "type": "object",
                "properties": {"limit": {"type": "integer", "default": 5}},
            },
        },
    },
]


def _season_out_dict(player, season, club_names):
    return {
        "season": season.season,
        "club": club_names.get(season.club_id),
        "league": season.league,
        "age": season.age,
        "appearances": season.appearances,
        "minutes_played": season.minutes_played,
        "goals": season.goals,
        "assists": season.assists,
        "market_value_eur": season.market_value_in_eur,
    }


def _predict_for_season(db: Session, player, season):
    prestige = player_service.latest_club_prestige(db, season.club_id) if season.club_id else None
    if prestige is None:
        prestige = player_service.league_average_prestige(db, season.league)
    payload = {
        "age": season.age, "sub_position": player.sub_position, "foot": player.foot, "league": season.league,
        "appearances": season.appearances, "minutes_played": season.minutes_played,
        "goals": season.goals, "assists": season.assists,
        "yellow_cards": season.yellow_cards, "red_cards": season.red_cards,
    }
    return ml_service.predict_market_value(payload, prestige, player.height_in_cm or 180.0)


def _tool_search_players(db: Session, name: str, limit: int = 5):
    rows, _, club_names = player_service.search_players(db, name=name, limit=limit)
    return {
        "results": [
            {
                "name": p.name, "club": club_names.get(s.club_id), "position": p.position,
                "age": s.age, "market_value_eur": s.market_value_in_eur,
            }
            for p, s in rows
        ]
    }


def _tool_get_player_detail(db: Session, name: str):
    rows, _, club_names = player_service.search_players(db, name=name, limit=1)
    if not rows:
        return {"error": f"No player found matching '{name}'"}
    player, latest = rows[0]
    predicted = _predict_for_season(db, player, latest)
    diff_pct = (predicted - latest.market_value_in_eur) / latest.market_value_in_eur if latest.market_value_in_eur else 0
    return {
        "name": player.name, "position": player.sub_position, "foot": player.foot,
        "latest_season": _season_out_dict(player, latest, club_names),
        "predicted_value_eur": predicted,
        "difference_pct": diff_pct,
        "note": "predicted_value_eur is a statistical model estimate, not an official valuation",
    }


def _tool_top_players(db: Session, limit: int = 5, position: str = None):
    rows, _, club_names = player_service.search_players(db, position=position, limit=limit)
    return {
        "results": [
            {"name": p.name, "club": club_names.get(s.club_id), "market_value_eur": s.market_value_in_eur}
            for p, s in rows
        ]
    }


def _tool_undervalued_players(db: Session, limit: int = 5):
    # scan among the top 150 most valuable players (the pool where "undervalued
    # vs. the model" is a meaningful, interesting signal) rather than the full
    # 10k+ roster, which would be slow and mostly noise at low values
    rows, _, club_names = player_service.search_players(db, sort_by="market_value_in_eur", descending=True, limit=150)
    results = []
    for player, season in rows:
        predicted = _predict_for_season(db, player, season)
        diff_pct = (predicted - season.market_value_in_eur) / season.market_value_in_eur if season.market_value_in_eur else 0
        results.append({
            "name": player.name, "club": club_names.get(season.club_id),
            "market_value_eur": season.market_value_in_eur, "predicted_value_eur": predicted,
            "difference_pct": diff_pct,
        })
    results.sort(key=lambda r: r["difference_pct"], reverse=True)
    return {"results": results[:limit]}


TOOL_EXECUTORS = {
    "search_players": _tool_search_players,
    "get_player_detail": _tool_get_player_detail,
    "top_players": _tool_top_players,
    "undervalued_players": _tool_undervalued_players,
}


def run_chat(db: Session, message: str, history: list = None):
    """history: list of {"role": "user"|"assistant", "content": str} prior turns."""
    history = history or []

    rag_hits = rag_service.retrieve(message)
    system_content = SYSTEM_PROMPT
    if rag_hits:
        context_block = "\n\n".join(f"### {h['title']}\n{h['text']}" for h in rag_hits)
        system_content += f"\n\nRelevant knowledge-base context:\n\n{context_block}"

    messages = [{"role": "system", "content": system_content}]
    messages.extend(history)
    messages.append({"role": "user", "content": message})

    provider = llm_service.get_provider()

    for _ in range(MAX_TOOL_ROUNDS):
        response = provider.chat(messages, tools=TOOLS_SCHEMA)

        if not response.tool_calls:
            return {
                "reply": response.content or "",
                "sources": [{"source": h["source"], "title": h["title"]} for h in rag_hits],
            }

        # OpenAI requires the assistant tool-call message echoed back before tool results
        messages.append({
            "role": "assistant",
            "content": response.content,
            "tool_calls": [
                {"id": tc.id, "type": "function", "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)}}
                for tc in response.tool_calls
            ],
        })

        for tc in response.tool_calls:
            executor = TOOL_EXECUTORS.get(tc.name)
            result = executor(db, **tc.arguments) if executor else {"error": f"Unknown tool: {tc.name}"}
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})

    return {
        "reply": "I wasn't able to finish looking that up - could you try rephrasing?",
        "sources": [],
    }
