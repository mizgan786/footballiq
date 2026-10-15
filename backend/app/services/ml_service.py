"""
ml_service.py

Loads the trained pipeline once (imported at module load time - FastAPI's
startup event just triggers this import, it never reloads per-request).

build_feature_vector() mirrors the encoding done in
scripts/feature_engineering.py exactly: same numeric columns, same
one-hot prefixes, reindexed to the exact column order the model was
trained on (missing dummy columns -> 0, so an unseen category doesn't
crash the app, it just contributes no signal for that column).
"""

import os
import numpy as np
import pandas as pd
import joblib

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "models", "trained_model.pkl")

_bundle = joblib.load(MODEL_PATH)
PIPELINE = _bundle["pipeline"]
FEATURE_COLUMNS = _bundle["feature_columns"]
MODEL_NAME = _bundle["model_name"]

NUMERIC_FEATURES = [
    "age", "height_in_cm", "appearances", "minutes_played",
    "goals", "assists", "goals_per_90", "assists_per_90",
    "yellow_cards", "red_cards", "club_prestige_log",
]


def build_feature_vector(payload: dict, club_prestige_log: float, height_in_cm: float) -> pd.DataFrame:
    """payload: dict with age, sub_position, foot, league, appearances,
    minutes_played, goals, assists, yellow_cards, red_cards (as in
    schemas.PredictRequest). Returns a single-row DataFrame with exactly
    FEATURE_COLUMNS, in order."""

    minutes = max(payload["minutes_played"], 1)
    goals_per_90 = payload["goals"] / minutes * 90
    assists_per_90 = payload["assists"] / minutes * 90

    row = {
        "age": payload["age"],
        "height_in_cm": height_in_cm,
        "appearances": payload["appearances"],
        "minutes_played": payload["minutes_played"],
        "goals": payload["goals"],
        "assists": payload["assists"],
        "goals_per_90": goals_per_90,
        "assists_per_90": assists_per_90,
        "yellow_cards": payload["yellow_cards"],
        "red_cards": payload["red_cards"],
        "club_prestige_log": club_prestige_log,
        f"subpos_{payload['sub_position']}": 1,
        f"foot_{payload['foot']}": 1,
        f"league_{payload['league']}": 1,
    }
    df = pd.DataFrame([row])
    df = df.reindex(columns=FEATURE_COLUMNS, fill_value=0)
    return df


def predict_market_value(payload: dict, club_prestige_log: float, height_in_cm: float) -> float:
    X = build_feature_vector(payload, club_prestige_log, height_in_cm)
    log_pred = PIPELINE.predict(X)[0]
    return float(np.exp(log_pred))


def top_feature_names(n: int = 5) -> list:
    model = PIPELINE.named_steps["model"]
    if not hasattr(model, "feature_importances_"):
        return []
    importances = pd.Series(model.feature_importances_, index=FEATURE_COLUMNS)
    return importances.sort_values(ascending=False).head(n).index.tolist()
