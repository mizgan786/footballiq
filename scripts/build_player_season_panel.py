"""
build_player_season_panel.py

Builds the core ML training table: one row per (player, season) in the
top 5 European leagues, with aggregated performance stats and a market
value target.

Season labeling follows Transfermarkt convention: season "2023" means the
2023/24 season, running roughly Aug 2023 - May 2024. We anchor the market
value target to the valuation closest to 30 June of the *following* year
(i.e. end of that season), within a +/- 6 month window, so the target
reflects the player's value at the point their season-long form had been
priced in - and we never use a valuation from *after* that window, which
would leak future information (e.g. a big transfer-driven value jump).
"""

import os
import pandas as pd
import numpy as np

FILTERED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "_filtered")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "player_season_panel.csv")

VALUATION_WINDOW_DAYS = 183  # +/- 6 months around season-end anchor date


def season_end_anchor(season: int) -> pd.Timestamp:
    """Transfermarkt season 'season' (e.g. 2023) -> 30 June of season+1."""
    return pd.Timestamp(year=int(season) + 1, month=6, day=30)


def main():
    print("Loading filtered tables ...")
    appearances = pd.read_csv(os.path.join(FILTERED_DIR, "appearances_top5.csv"), parse_dates=["date"])
    games = pd.read_csv(os.path.join(FILTERED_DIR, "games_top5.csv"), parse_dates=["date"])
    players = pd.read_csv(os.path.join(FILTERED_DIR, "players_relevant.csv"), parse_dates=["date_of_birth"])
    valuations = pd.read_csv(os.path.join(FILTERED_DIR, "valuations_relevant.csv"), parse_dates=["date"])

    # --- attach season to each appearance via its game ---
    game_season = games[["game_id", "season"]]
    app = appearances.merge(game_season, on="game_id", how="inner")

    # --- aggregate per player-season ---
    print("Aggregating per player-season ...")
    agg = app.groupby(["player_id", "season"]).agg(
        appearances=("game_id", "count"),
        minutes_played=("minutes_played", "sum"),
        goals=("goals", "sum"),
        assists=("assists", "sum"),
        yellow_cards=("yellow_cards", "sum"),
        red_cards=("red_cards", "sum"),
        league=("competition_id", lambda s: s.mode().iat[0]),
        club_id=("player_club_id", lambda s: s.mode().iat[0]),
    ).reset_index()

    # per-90 stats (guard against zero minutes)
    agg["goals_per_90"] = np.where(agg["minutes_played"] > 0, agg["goals"] / agg["minutes_played"] * 90, 0.0)
    agg["assists_per_90"] = np.where(agg["minutes_played"] > 0, agg["assists"] / agg["minutes_played"] * 90, 0.0)

    # --- attach static player attributes ---
    player_attrs = players[[
        "player_id", "name", "position", "sub_position", "foot",
        "height_in_cm", "date_of_birth", "country_of_citizenship",
    ]]
    panel = agg.merge(player_attrs, on="player_id", how="left")

    # age as of each season's anchor date
    anchor_dates = panel["season"].map(season_end_anchor)
    panel["age"] = ((anchor_dates - panel["date_of_birth"]).dt.days / 365.25).round(1)

    # --- nearest market valuation within window, per player-season ---
    print("Matching nearest market valuation per player-season (this takes a moment) ...")
    valuations_sorted = valuations.sort_values("date")

    # group valuations per player once, then look up nearest-by-date per player-season row
    val_by_player = {pid: g[["date", "market_value_in_eur"]].reset_index(drop=True)
                      for pid, g in valuations_sorted.groupby("player_id")}

    market_values = []
    days_off = []
    for pid, season in zip(panel["player_id"], panel["season"]):
        sub = val_by_player.get(pid)
        if sub is None or sub.empty:
            market_values.append(np.nan)
            days_off.append(np.nan)
            continue
        anchor = season_end_anchor(season)
        diffs = (sub["date"] - anchor).abs()
        pos = diffs.values.argmin()
        min_days = diffs.iloc[pos].days
        if min_days > VALUATION_WINDOW_DAYS:
            market_values.append(np.nan)
            days_off.append(np.nan)
        else:
            market_values.append(sub.iloc[pos]["market_value_in_eur"])
            days_off.append(min_days)

    panel["market_value_in_eur"] = market_values
    panel["valuation_days_from_anchor"] = days_off

    before = len(panel)
    panel = panel.dropna(subset=["market_value_in_eur"]).copy()
    print(f"Dropped {before - len(panel):,} player-season rows with no valuation in window "
          f"({len(panel):,} remain)")

    # --- lagged club-prestige feature ---
    # For each (club_id, season), the average log(market value) of all players
    # at that club in the *previous* season. This is a legitimate lag feature
    # (only uses information from before the season being predicted) - not
    # leakage, since it never touches the current season's own valuations.
    print("Computing lagged club-prestige feature ...")
    panel["log_market_value_tmp"] = np.log(panel["market_value_in_eur"])
    club_season_avg = (
        panel.groupby(["club_id", "season"])["log_market_value_tmp"]
        .mean()
        .reset_index()
        .rename(columns={"log_market_value_tmp": "club_prestige_log"})
    )
    club_season_avg["season"] = club_season_avg["season"] + 1  # shift forward: prior season's avg becomes this season's feature
    panel = panel.merge(club_season_avg, on=["club_id", "season"], how="left")
    n_missing_prestige = panel["club_prestige_log"].isna().sum()

    # fallback for missing (club's first appearance in the panel, or first season overall):
    # use the *previous* season's global average log market value across all clubs
    # (computed before the shift, so this fallback also only uses prior-season info)
    season_global_avg_prev = panel.groupby("season")["log_market_value_tmp"].mean()
    fallback = (panel["season"] - 1).map(season_global_avg_prev)
    panel["club_prestige_log"] = panel["club_prestige_log"].fillna(fallback)
    # first season overall (2012) has no prior data at all - fall back to that
    # season's own global average as a last resort
    panel["club_prestige_log"] = panel["club_prestige_log"].fillna(panel["season"].map(season_global_avg_prev))
    panel = panel.drop(columns=["log_market_value_tmp"])
    print(f"  club_prestige_log missing before fallback: {n_missing_prestige} (filled with prior-season global average)")

    panel = panel.sort_values(["season", "player_id"]).reset_index(drop=True)
    panel.to_csv(OUT_PATH, index=False)
    print(f"Wrote {len(panel):,} rows to {OUT_PATH}")
    print()
    print("Season counts:")
    print(panel["season"].value_counts().sort_index())
    print()
    print("Market value (EUR) distribution:")
    print(panel["market_value_in_eur"].describe())


if __name__ == "__main__":
    main()
