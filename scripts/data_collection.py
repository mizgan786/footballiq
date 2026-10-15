"""
data_collection.py

Loads raw Transfermarkt tables from data/raw/ and filters them down to the
top 5 European leagues (Premier League, La Liga, Bundesliga, Serie A, Ligue 1).

Output: filtered CSVs written to data/processed/_filtered/, used as input
to build_player_season_panel.py.
"""

import os
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "_filtered")

TOP5_COMPETITIONS = ["GB1", "ES1", "L1", "IT1", "FR1"]  # Premier League, La Liga, Bundesliga, Serie A, Ligue 1


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    print("Loading games.csv ...")
    games = pd.read_csv(
        os.path.join(RAW_DIR, "games.csv"),
        usecols=["game_id", "competition_id", "season", "date"],
    )
    games_top5 = games[games["competition_id"].isin(TOP5_COMPETITIONS)].copy()
    print(f"  {len(games_top5):,} / {len(games):,} games are in the top 5 leagues")
    games_top5.to_csv(os.path.join(OUT_DIR, "games_top5.csv"), index=False)

    print("Loading appearances.csv (this is the big one) ...")
    appearances = pd.read_csv(
        os.path.join(RAW_DIR, "appearances.csv"),
        usecols=[
            "player_id", "game_id", "date", "player_name", "competition_id",
            "player_club_id", "yellow_cards", "red_cards", "goals", "assists", "minutes_played",
        ],
    )
    # keep only appearances that belong to a top-5-league game
    appearances_top5 = appearances[appearances["game_id"].isin(games_top5["game_id"])].copy()
    print(f"  {len(appearances_top5):,} / {len(appearances):,} appearances are in top-5-league games")
    appearances_top5.to_csv(os.path.join(OUT_DIR, "appearances_top5.csv"), index=False)

    print("Loading players.csv ...")
    players = pd.read_csv(os.path.join(RAW_DIR, "players.csv"))
    relevant_player_ids = set(appearances_top5["player_id"].unique())
    players_relevant = players[players["player_id"].isin(relevant_player_ids)].copy()
    print(f"  {len(players_relevant):,} / {len(players):,} players have at least one top-5-league appearance")
    players_relevant.to_csv(os.path.join(OUT_DIR, "players_relevant.csv"), index=False)

    print("Loading player_valuations.csv ...")
    valuations = pd.read_csv(os.path.join(RAW_DIR, "player_valuations.csv"))
    valuations_relevant = valuations[valuations["player_id"].isin(relevant_player_ids)].copy()
    print(f"  {len(valuations_relevant):,} / {len(valuations):,} valuation records kept")
    valuations_relevant.to_csv(os.path.join(OUT_DIR, "valuations_relevant.csv"), index=False)

    print("Loading clubs.csv ...")
    clubs = pd.read_csv(os.path.join(RAW_DIR, "clubs.csv"))
    clubs_top5 = clubs[clubs["domestic_competition_id"].isin(TOP5_COMPETITIONS)].copy()
    clubs_top5.to_csv(os.path.join(OUT_DIR, "clubs_top5.csv"), index=False)

    print("Done. Filtered files written to", OUT_DIR)


if __name__ == "__main__":
    main()
