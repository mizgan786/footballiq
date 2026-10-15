from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.services import player_service, ml_service
from app.schemas.schemas import CompareRequest, CompareResponse, ComparePlayerResult, PlayerSeasonOut

router = APIRouter(prefix="/api", tags=["compare"])


def _compare_result(db: Session, player_id: int) -> ComparePlayerResult:
    result = player_service.get_player_detail(db, player_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Player {player_id} not found")
    player, seasons, club_names = result
    if not seasons:
        raise HTTPException(status_code=404, detail=f"Player {player_id} has no season data")
    latest = seasons[-1]

    season_out = PlayerSeasonOut(
        season=latest.season, league=latest.league, club_id=latest.club_id,
        club_name=club_names.get(latest.club_id), age=latest.age, appearances=latest.appearances,
        minutes_played=latest.minutes_played, goals=latest.goals, assists=latest.assists,
        goals_per_90=latest.goals_per_90, assists_per_90=latest.assists_per_90,
        yellow_cards=latest.yellow_cards, red_cards=latest.red_cards,
        market_value_in_eur=latest.market_value_in_eur,
    )

    # run the model on this player's own latest-season stats, same as the profile page
    prestige = player_service.latest_club_prestige(db, latest.club_id) if latest.club_id else None
    if prestige is None:
        prestige = player_service.league_average_prestige(db, latest.league)
    payload = {
        "age": latest.age, "sub_position": player.sub_position, "foot": player.foot, "league": latest.league,
        "appearances": latest.appearances, "minutes_played": latest.minutes_played,
        "goals": latest.goals, "assists": latest.assists,
        "yellow_cards": latest.yellow_cards, "red_cards": latest.red_cards,
    }
    predicted = ml_service.predict_market_value(payload, prestige, player.height_in_cm or 180.0)
    diff = predicted - latest.market_value_in_eur
    diff_pct = diff / latest.market_value_in_eur if latest.market_value_in_eur else 0.0

    return ComparePlayerResult(
        id=player.id, name=player.name, position=player.position, sub_position=player.sub_position,
        latest_season=season_out, predicted_value_eur=predicted, difference_eur=diff, difference_pct=diff_pct,
    )


@router.post("/compare", response_model=CompareResponse)
def compare_players(payload: CompareRequest, db: Session = Depends(get_db)):
    return CompareResponse(
        player_a=_compare_result(db, payload.player_id_a),
        player_b=_compare_result(db, payload.player_id_b),
    )
