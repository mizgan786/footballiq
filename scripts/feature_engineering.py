"""
feature_engineering.py

Takes the clean player-season panel and builds the final model-ready
feature table:

  - One-hot encodes `sub_position` (13 categories - e.g. Centre-Back,
    Right Winger) rather than the coarse `position` (4 categories), since
    sub-position captures real value differences a coarse label would
    average away (e.g. a Centre-Back and a Right-Back get very different
    valuations for the same defensive stats).
  - One-hot encodes `foot` (left / right / both).
  - Keeps numeric features as-is: age, height_in_cm, appearances,
    minutes_played, goals, assists, goals_per_90, assists_per_90,
    yellow_cards, red_cards.
  - Keeps identifiers/target separately (not fed to the model as features):
    player_id, name, season, market_value_in_eur, log_market_value.

Output: data/processed/model_features.csv
  - One column per encoded category, prefixed (subpos_..., foot_...)
  - A `feature_columns.txt` sidecar listing exactly which columns are
    model inputs, so train_model.py doesn't have to guess.
"""

import os
import pandas as pd

IN_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "player_season_panel_clean.csv")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "model_features.csv")
FEATURE_LIST_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "feature_columns.txt")

NUMERIC_FEATURES = [
    "age", "height_in_cm", "appearances", "minutes_played",
    "goals", "assists", "goals_per_90", "assists_per_90",
    "yellow_cards", "red_cards", "club_prestige_log",
]
ID_AND_TARGET_COLUMNS = [
    "player_id", "name", "season", "market_value_in_eur", "log_market_value",
]


def main():
    df = pd.read_csv(IN_PATH)

    subpos_dummies = pd.get_dummies(df["sub_position"], prefix="subpos")
    foot_dummies = pd.get_dummies(df["foot"], prefix="foot")
    league_dummies = pd.get_dummies(df["league"], prefix="league")

    features = pd.concat(
        [df[ID_AND_TARGET_COLUMNS], df[NUMERIC_FEATURES], subpos_dummies, foot_dummies, league_dummies],
        axis=1,
    )

    model_input_columns = (
        NUMERIC_FEATURES + list(subpos_dummies.columns) + list(foot_dummies.columns) + list(league_dummies.columns)
    )

    features.to_csv(OUT_PATH, index=False)
    with open(FEATURE_LIST_PATH, "w") as f:
        f.write("\n".join(model_input_columns))

    print(f"Wrote {len(features):,} rows x {len(features.columns)} columns to {OUT_PATH}")
    print(f"Model input features ({len(model_input_columns)}):")
    for c in model_input_columns:
        print(f"  - {c}")


if __name__ == "__main__":
    main()
