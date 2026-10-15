"""
data_cleaning.py

Cleans data/processed/player_season_panel.csv:
  - Drops the tiny number of rows with unknown position (17 rows, 0.05%)
    - too small a group to model reliably, and it's a data-entry gap, not
      a real category.
  - Imputes missing `foot` with the modal value ('right', ~74% of players).
  - Imputes missing `height_in_cm` with the position-specific median
    (goalkeepers/defenders run taller than attackers/midfielders, so a
    global median would bias those rows).
  - Adds `log_market_value` (natural log of the target). Market value is
    heavily right-skewed (many low-value squad players, a long tail of
    superstars) - training on the raw euro value would let a handful of
    150M+ outliers dominate the loss. Models are trained on the log target;
    predictions are exponentiated back to euros at inference time.
  - Sanity-checks for duplicate (player_id, season) rows (should be none,
    by construction of the groupby in build_player_season_panel.py).

Output: data/processed/player_season_panel_clean.csv
"""

import os
import numpy as np
import pandas as pd

IN_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "player_season_panel.csv")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "player_season_panel_clean.csv")


def main():
    df = pd.read_csv(IN_PATH)
    n_start = len(df)

    # duplicate check
    dupes = df.duplicated(subset=["player_id", "season"]).sum()
    if dupes:
        print(f"WARNING: {dupes} duplicate (player_id, season) rows found - dropping extras")
        df = df.drop_duplicates(subset=["player_id", "season"])

    # drop unusable position rows
    df = df[df["position"] != "Missing"].copy()
    print(f"Dropped {n_start - len(df)} rows with missing/unknown position")

    # impute foot with mode
    mode_foot = df["foot"].mode(dropna=True)[0]
    n_missing_foot = df["foot"].isna().sum()
    df["foot"] = df["foot"].fillna(mode_foot)
    print(f"Imputed {n_missing_foot} missing 'foot' values with mode ('{mode_foot}')")

    # impute height with position-specific median
    n_missing_height = df["height_in_cm"].isna().sum()
    df["height_in_cm"] = df.groupby("position")["height_in_cm"].transform(lambda s: s.fillna(s.median()))
    print(f"Imputed {n_missing_height} missing 'height_in_cm' values with position-median")

    # age is a core feature - drop the handful of rows missing date_of_birth
    # (can't compute age for them) rather than impute something as important as age
    n_missing_age = df["age"].isna().sum()
    df = df[df["age"].notna()].copy()
    print(f"Dropped {n_missing_age} rows with missing date_of_birth (can't compute age)")

    # nationality isn't a core model feature but is kept for the player-profile UI;
    # fill rather than drop rows over it
    df["country_of_citizenship"] = df["country_of_citizenship"].fillna("Unknown")

    # log target for skew
    df["log_market_value"] = np.log(df["market_value_in_eur"])

    df = df.reset_index(drop=True)
    df.to_csv(OUT_PATH, index=False)
    print(f"\nWrote {len(df):,} clean rows to {OUT_PATH}")
    print("\nRemaining nulls (should be none):")
    print(df.isna().sum()[df.isna().sum() > 0])


if __name__ == "__main__":
    main()
