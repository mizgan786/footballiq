from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.orm import Player, PlayerSeasonStats, Club


def _club_name_map(db: Session, club_ids: set) -> dict:
    if not club_ids:
        return {}
    rows = db.query(Club.id, Club.name).filter(Club.id.in_(club_ids)).all()
    return {cid: name for cid, name in rows}


def search_players(
    db: Session,
    name: Optional[str] = None,
    position: Optional[str] = None,
    club_id: Optional[int] = None,
    min_age: Optional[float] = None,
    max_age: Optional[float] = None,
    sort_by: str = "market_value_in_eur",
    descending: bool = True,
    limit: int = 50,
    offset: int = 0,
):
    """Returns each player's most recent season row, filtered/sorted as requested."""
    latest_season_subq = (
        db.query(
            PlayerSeasonStats.player_id,
            func.max(PlayerSeasonStats.season).label("max_season"),
        )
        .group_by(PlayerSeasonStats.player_id)
        .subquery()
    )

    q = (
        db.query(Player, PlayerSeasonStats)
        .join(PlayerSeasonStats, Player.id == PlayerSeasonStats.player_id)
        .join(
            latest_season_subq,
            (PlayerSeasonStats.player_id == latest_season_subq.c.player_id)
            & (PlayerSeasonStats.season == latest_season_subq.c.max_season),
        )
    )

    if name:
        q = q.filter(Player.name.ilike(f"%{name}%"))
    if position:
        q = q.filter(Player.position == position)
    if club_id is not None:
        q = q.filter(PlayerSeasonStats.club_id == club_id)
    if min_age is not None:
        q = q.filter(PlayerSeasonStats.age >= min_age)
    if max_age is not None:
        q = q.filter(PlayerSeasonStats.age <= max_age)

    sort_col = getattr(PlayerSeasonStats, sort_by, PlayerSeasonStats.market_value_in_eur)
    q = q.order_by(sort_col.desc() if descending else sort_col.asc())

    total = q.count()
    rows = q.offset(offset).limit(limit).all()

    club_names = _club_name_map(db, {s.club_id for _, s in rows if s.club_id is not None})
    return rows, total, club_names


def get_player_detail(db: Session, player_id: int):
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        return None
    seasons = (
        db.query(PlayerSeasonStats)
        .filter(PlayerSeasonStats.player_id == player_id)
        .order_by(PlayerSeasonStats.season.asc())
        .all()
    )
    club_names = _club_name_map(db, {s.club_id for s in seasons if s.club_id is not None})
    return player, seasons, club_names


def latest_club_prestige(db: Session, club_id: int) -> Optional[float]:
    row = (
        db.query(PlayerSeasonStats.club_prestige_log)
        .filter(PlayerSeasonStats.club_id == club_id)
        .order_by(PlayerSeasonStats.season.desc())
        .first()
    )
    return row[0] if row else None


def league_average_prestige(db: Session, league: str) -> float:
    avg = (
        db.query(func.avg(PlayerSeasonStats.club_prestige_log))
        .filter(PlayerSeasonStats.league == league)
        .scalar()
    )
    return float(avg) if avg is not None else 0.0


def top_players(db: Session, limit: int = 10):
    return search_players(db, sort_by="market_value_in_eur", descending=True, limit=limit)


def list_clubs(db: Session):
    return db.query(Club).order_by(Club.name.asc()).all()


def analytics_summary(db: Session):
    rows, total_players, club_names = search_players(db, limit=1_000_000)  # dataset is small enough for this
    avg_value = sum(s.market_value_in_eur for _, s in rows) / len(rows) if rows else 0.0
    top_player, top_stats = max(rows, key=lambda ps: ps[1].market_value_in_eur)
    seasons = sorted({s.season for _, s in rows})
    return {
        "players_analyzed": total_players,
        "seasons_covered": seasons,
        "average_market_value_eur": avg_value,
        "highest_valued_player": {
            "id": top_player.id,
            "name": top_player.name,
            "position": top_player.position,
            "club_id": top_stats.club_id,
            "club_name": club_names.get(top_stats.club_id),
            "season": top_stats.season,
            "age": top_stats.age,
            "market_value_in_eur": top_stats.market_value_in_eur,
        },
    }
