"""
Sanity tests for the processed data pipeline outputs (data_cleaning.py /
feature_engineering.py). Runs against the already-built processed files
rather than re-running the full pipeline (that takes minutes and needs
the raw CSVs) - if these files exist, they should meet these invariants.
"""
import os
import pandas as pd

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


def test_clean_panel_has_no_nulls():
    df = pd.read_csv(os.path.join(PROCESSED_DIR, "player_season_panel_clean.csv"))
    assert df.isna().sum().sum() == 0


def test_clean_panel_market_value_positive():
    df = pd.read_csv(os.path.join(PROCESSED_DIR, "player_season_panel_clean.csv"))
    assert (df["market_value_in_eur"] > 0).all()


def test_model_features_match_feature_columns_file():
    features = pd.read_csv(os.path.join(PROCESSED_DIR, "model_features.csv"))
    with open(os.path.join(PROCESSED_DIR, "feature_columns.txt")) as f:
        cols = [line.strip() for line in f if line.strip()]
    assert all(c in features.columns for c in cols)


def test_no_duplicate_player_seasons():
    df = pd.read_csv(os.path.join(PROCESSED_DIR, "player_season_panel_clean.csv"))
    assert not df.duplicated(subset=["player_id", "season"]).any()
