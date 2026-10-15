from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database.db import Base


class Club(Base):
    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True)  # transfermarkt club_id
    name = Column(String, nullable=False, index=True)
    domestic_competition_id = Column(String)
    stadium_name = Column(String)


class Player(Base):
    """One row per player - static-ish attributes (name, position, physical
    profile). Season-by-season performance/value lives in PlayerSeasonStats."""
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)  # transfermarkt player_id
    name = Column(String, index=True, nullable=False)
    position = Column(String)
    sub_position = Column(String)
    foot = Column(String)
    height_in_cm = Column(Float)
    date_of_birth = Column(String)
    nationality = Column(String)

    seasons = relationship("PlayerSeasonStats", back_populates="player")


class PlayerSeasonStats(Base):
    """One row per (player, season): performance stats, club/league context,
    and the market value used as the ML target."""
    __tablename__ = "player_statistics"
    __table_args__ = (UniqueConstraint("player_id", "season", name="uq_player_season"),)

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    season = Column(Integer, nullable=False, index=True)
    league = Column(String)
    club_id = Column(Integer)
    age = Column(Float)

    appearances = Column(Integer)
    minutes_played = Column(Integer)
    goals = Column(Integer)
    assists = Column(Integer)
    goals_per_90 = Column(Float)
    assists_per_90 = Column(Float)
    yellow_cards = Column(Integer)
    red_cards = Column(Integer)

    club_prestige_log = Column(Float)
    market_value_in_eur = Column(Float)

    player = relationship("Player", back_populates="seasons")


class Prediction(Base):
    """Log of every prediction served by POST /api/predict, for auditability
    and so the frontend can show 'model estimate as of <timestamp>'."""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=True)  # null for hypothetical/what-if inputs
    predicted_value_eur = Column(Float, nullable=False)
    model_version = Column(String, nullable=False)
    input_payload = Column(String)  # JSON-encoded request, for reproducibility
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
