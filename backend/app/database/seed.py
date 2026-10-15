"""
seed.py

One-time (idempotent) load of clubs + the processed player-season panel
into the clubs / players / player_statistics tables. Run directly:

    cd backend && python -m app.database.seed
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))  # allow `import app...`

import pandas as pd
from app.database.db import Base, engine, SessionLocal
from app.models.orm import Club, Player, PlayerSeasonStats

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "processed")
PANEL_PATH = os.path.join(DATA_DIR, "player_season_panel_clean.csv")
CLUBS_PATH = os.path.join(DATA_DIR, "clubs_top5.csv")


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    already_seeded = db.query(Player).first() is not None
    if already_seeded:
        print("DB already has players - skipping seed. Delete footballiq.db (or drop tables) to reseed from scratch.")
        db.close()
        return

    # --- clubs ---
    clubs_df = pd.read_csv(CLUBS_PATH)
    clubs = [
        Club(
            id=int(row.club_id),
            name=row.name,
            domestic_competition_id=row.domestic_competition_id,
            stadium_name=row.stadium_name if not pd.isna(row.stadium_name) else None,
        )
        for row in clubs_df.itertuples()
    ]
    db.bulk_save_objects(clubs)
    db.commit()
    print(f"Inserted {len(clubs):,} clubs")

    # --- players + player_statistics ---
    df = pd.read_csv(PANEL_PATH)
    print(f"Loading {len(df):,} player-season rows from {PANEL_PATH}")

    latest = df.sort_values("season").groupby("player_id").tail(1)
    players = [
        Player(
            id=int(row.player_id),
            name=row.name,
            position=row.position,
            sub_position=row.sub_position,
            foot=row.foot,
            height_in_cm=row.height_in_cm,
            date_of_birth=str(row.date_of_birth),
            nationality=row.country_of_citizenship,
        )
        for row in latest.itertuples()
    ]
    db.bulk_save_objects(players)
    db.commit()
    print(f"Inserted {len(players):,} players")

    stats = [
        PlayerSeasonStats(
            player_id=int(row.player_id),
            season=int(row.season),
            league=row.league,
            club_id=int(row.club_id) if not pd.isna(row.club_id) else None,
            age=row.age,
            appearances=int(row.appearances),
            minutes_played=int(row.minutes_played),
            goals=int(row.goals),
            assists=int(row.assists),
            goals_per_90=row.goals_per_90,
            assists_per_90=row.assists_per_90,
            yellow_cards=int(row.yellow_cards),
            red_cards=int(row.red_cards),
            club_prestige_log=row.club_prestige_log,
            market_value_in_eur=row.market_value_in_eur,
        )
        for row in df.itertuples()
    ]
    db.bulk_save_objects(stats)
    db.commit()
    print(f"Inserted {len(stats):,} player-season stat rows")
    db.close()


if __name__ == "__main__":
    main()
