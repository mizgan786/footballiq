"""
analytics_service.py

Every chart on the Analytics page is computed here from real data:
  - distribution / value_by_position / age_vs_value / goals_vs_value: queried
    from the player_statistics table (the actual training dataset - all
    35k+ player-seasons, not just the latest snapshot per player).
  - actual_vs_predicted: runs the trained model against a sample of the
    held-out test seasons (2023-2025) from model_features.csv, the same
    file evaluate_model.py used for the final test-set evaluation.
  - feature_importance: read from models/feature_importance.json, written
    by evaluate_model.py.

Scatter series are downsampled for the frontend (every Nth row, not
random) so results are deterministic across requests.
"""

import os
import json
import random
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.orm import Player, PlayerSeasonStats
from app.services import ml_service

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "processed")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "models")
FEATURE_IMPORTANCE_PATH = os.path.join(MODELS_DIR, "feature_importance.json")
MODEL_FEATURES_PATH = os.path.join(DATA_DIR, "model_features.csv")

VALUE_BUCKETS = [
    ("<1M", 0, 1_000_000),
    ("1-5M", 1_000_000, 5_000_000),
    ("5-10M", 5_000_000, 10_000_000),
    ("10-25M", 10_000_000, 25_000_000),
    ("25-50M", 25_000_000, 50_000_000),
    ("50M+", 50_000_000, float("inf")),
]

TEST_SEASONS = [2023, 2024, 2025]


def market_value_distribution(db: Session):
    counts = []
    for label, lo, hi in VALUE_BUCKETS:
        q = db.query(func.count(PlayerSeasonStats.id)).filter(PlayerSeasonStats.market_value_in_eur >= lo)
        if hi != float("inf"):
            q = q.filter(PlayerSeasonStats.market_value_in_eur < hi)
        counts.append({"bucket": label, "count": q.scalar()})
    return counts


def value_by_position(db: Session):
    rows = (
        db.query(Player.position, func.avg(PlayerSeasonStats.market_value_in_eur), func.count(PlayerSeasonStats.id))
        .join(PlayerSeasonStats, Player.id == PlayerSeasonStats.player_id)
        .group_by(Player.position)
        .all()
    )
    return [
        {"position": pos, "avg_market_value_eur": float(avg), "n": n}
        for pos, avg, n in rows
        if pos and pos != "Missing"
    ]


def _downsample(rows, target_n=600):
    if len(rows) <= target_n:
        return rows
    step = len(rows) // target_n
    return rows[::step][:target_n]


def age_vs_value(db: Session):
    rows = db.query(PlayerSeasonStats.age, PlayerSeasonStats.market_value_in_eur).all()
    rows = _downsample(rows)
    return [{"age": a, "market_value_eur": v} for a, v in rows]


def goals_vs_value(db: Session):
    rows = db.query(PlayerSeasonStats.goals, PlayerSeasonStats.market_value_in_eur).all()
    rows = _downsample(rows)
    return [{"goals": g, "market_value_eur": v} for g, v in rows]


def actual_vs_predicted(sample_size: int = 400):
    import pandas as pd
    import numpy as np

    df = pd.read_csv(MODEL_FEATURES_PATH)
    test = df[df["season"].isin(TEST_SEASONS)]
    if len(test) > sample_size:
        rng = random.Random(42)  # fixed seed - deterministic across requests
        idx = sorted(rng.sample(range(len(test)), sample_size))
        test = test.iloc[idx]

    X = test[ml_service.FEATURE_COLUMNS]
    pred_log = ml_service.PIPELINE.predict(X)
    actual = np.exp(test["log_market_value"].values)
    predicted = np.exp(pred_log)

    return [{"actual_eur": float(a), "predicted_eur": float(p)} for a, p in zip(actual, predicted)]


def feature_importance(top_n: int = 12):
    with open(FEATURE_IMPORTANCE_PATH) as f:
        data = json.load(f)
    items = sorted(data.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
    return [{"feature": k, "importance": v} for k, v in items]
