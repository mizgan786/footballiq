from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.services import player_service
from app.schemas.schemas import PlayerCardOut, PlayerDetailOut, PlayerSeasonOut

router = APIRouter(prefix="/api/players", tags=["players"])


@router.get("", response_model=list[PlayerCardOut])
def list_players(
    name: Optional[str] = None,
    position: Optional[str] = None,
    club_id: Optional[int] = None,
    min_age: Optional[float] = None,
    max_age: Optional[float] = None,
    sort_by: str = Query("market_value_in_eur", pattern="^(market_value_in_eur|age|goals|assists|appearances)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    rows, _, club_names = player_service.search_players(
        db, name=name, position=position, club_id=club_id, min_age=min_age, max_age=max_age,
        sort_by=sort_by, descending=(order == "desc"), limit=limit, offset=offset,
    )
    return [
        PlayerCardOut(
            id=p.id, name=p.name, position=p.position,
            club_id=s.club_id, club_name=club_names.get(s.club_id),
            season=s.season, age=s.age,
            market_value_in_eur=s.market_value_in_eur,
        )
        for p, s in rows
    ]


@router.get("/top", response_model=list[PlayerCardOut])
def top_players(limit: int = Query(10, le=100), db: Session = Depends(get_db)):
    rows, _, club_names = player_service.top_players(db, limit=limit)
    return [
        PlayerCardOut(
            id=p.id, name=p.name, position=p.position,
            club_id=s.club_id, club_name=club_names.get(s.club_id),
            season=s.season, age=s.age,
            market_value_in_eur=s.market_value_in_eur,
        )
        for p, s in rows
    ]


@router.get("/{player_id}", response_model=PlayerDetailOut)
def get_player(player_id: int, db: Session = Depends(get_db)):
    result = player_service.get_player_detail(db, player_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Player {player_id} not found")
    player, seasons, club_names = result
    return PlayerDetailOut(
        id=player.id, name=player.name, position=player.position, sub_position=player.sub_position,
        foot=player.foot, height_in_cm=player.height_in_cm, nationality=player.nationality,
        seasons=[
            PlayerSeasonOut(
                season=s.season, league=s.league, club_id=s.club_id, club_name=club_names.get(s.club_id),
                age=s.age, appearances=s.appearances, minutes_played=s.minutes_played,
                goals=s.goals, assists=s.assists, goals_per_90=s.goals_per_90, assists_per_90=s.assists_per_90,
                yellow_cards=s.yellow_cards, red_cards=s.red_cards, market_value_in_eur=s.market_value_in_eur,
            )
            for s in seasons
        ],
    )

