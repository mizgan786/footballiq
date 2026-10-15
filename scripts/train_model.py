"""
train_model.py

Time-aware split (no shuffling across seasons, so we never train on a
player's future-season data to predict their past-season value):

  train : seasons 2012-2020  (9 seasons, ~23k rows)
  val   : seasons 2021-2022  (2 seasons, ~5.2k rows)
  test  : seasons 2023-2025  (3 seasons, ~7.7k rows)  <- untouched until evaluate_model.py

Trains on log(market_value) to counter the heavy right-skew (see
data_cleaning.py). All reported metrics are converted back to euros
before comparison, since "MAE in log-space" isn't interpretable to a
non-technical reader of the README/portfolio.

Models compared on the validation set: Linear Regression (baseline),
Ridge, Random Forest, Gradient Boosting, XGBoost. The best model by
validation MAE is refit on train+val and saved for evaluate_model.py
to score, once, on the held-out test set.
"""

import os
import json
import numpy as np
import pandas as pd
import joblib

from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
import xgboost as xgb

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
FEATURES_PATH = os.path.join(DATA_DIR, "model_features.csv")
FEATURE_LIST_PATH = os.path.join(DATA_DIR, "feature_columns.txt")

TRAIN_SEASONS = list(range(2012, 2021))  # 2012-2020
VAL_SEASONS = [2021, 2022]
TEST_SEASONS = [2023, 2024, 2025]


def load_data():
    df = pd.read_csv(FEATURES_PATH)
    with open(FEATURE_LIST_PATH) as f:
        feature_cols = [line.strip() for line in f if line.strip()]
    return df, feature_cols


def split(df):
    train = df[df["season"].isin(TRAIN_SEASONS)]
    val = df[df["season"].isin(VAL_SEASONS)]
    test = df[df["season"].isin(TEST_SEASONS)]
    print(f"train: {len(train):,} rows | val: {len(val):,} rows | test: {len(test):,} rows")
    return train, val, test


def eval_in_euros(y_true_log, y_pred_log):
    y_true = np.exp(y_true_log)
    y_pred = np.exp(y_pred_log)
    return {
        "MAE_eur": mean_absolute_error(y_true, y_pred),
        "RMSE_eur": np.sqrt(mean_squared_error(y_true, y_pred)),
        "R2": r2_score(y_true, y_pred),
        "MAPE": mean_absolute_percentage_error(y_true, y_pred),
    }


def build_models():
    # linear models need scaled features; tree ensembles don't, but scaling
    # does no harm, so every model goes through the same pipeline shape for
    # a fair, simple comparison.
    return {
        "linear_regression": Pipeline([("scaler", StandardScaler()), ("model", LinearRegression())]),
        "ridge": Pipeline([("scaler", StandardScaler()), ("model", Ridge(alpha=1.0))]),
        "random_forest": Pipeline([("scaler", StandardScaler()),
                                    ("model", RandomForestRegressor(n_estimators=300, max_depth=12,
                                                                     min_samples_leaf=3, random_state=42, n_jobs=-1))]),
        "gradient_boosting": Pipeline([("scaler", StandardScaler()),
                                        ("model", GradientBoostingRegressor(n_estimators=300, max_depth=3,
                                                                             learning_rate=0.05, random_state=42))]),
        "xgboost": Pipeline([("scaler", StandardScaler()),
                              ("model", xgb.XGBRegressor(n_estimators=400, max_depth=5, learning_rate=0.05,
                                                          subsample=0.8, colsample_bytree=0.8,
                                                          random_state=42, n_jobs=-1))]),
    }


def main():
    os.makedirs(MODELS_DIR, exist_ok=True)
    df, feature_cols = load_data()
    train, val, test = split(df)

    X_train, y_train = train[feature_cols], train["log_market_value"]
    X_val, y_val = val[feature_cols], val["log_market_value"]

    models = build_models()
    results = {}
    fitted = {}

    print("\nTraining and evaluating on validation set (2021-2022):\n")
    for name, pipe in models.items():
        pipe.fit(X_train, y_train)
        val_pred_log = pipe.predict(X_val)
        metrics = eval_in_euros(y_val.values, val_pred_log)
        results[name] = metrics
        fitted[name] = pipe
        print(f"  {name:20s}  MAE=\u20ac{metrics['MAE_eur']:>10,.0f}  RMSE=\u20ac{metrics['RMSE_eur']:>10,.0f}  "
              f"R2={metrics['R2']:.3f}  MAPE={metrics['MAPE']:.1%}")

    best_name = min(results, key=lambda k: results[k]["MAE_eur"])
    print(f"\nBest model on validation MAE: {best_name}")

    # refit best model on train + val before final test evaluation
    train_val = pd.concat([train, val])
    X_train_val, y_train_val = train_val[feature_cols], train_val["log_market_value"]
    best_pipe = build_models()[best_name]
    best_pipe.fit(X_train_val, y_train_val)

    joblib.dump({"pipeline": best_pipe, "feature_columns": feature_cols, "model_name": best_name},
                os.path.join(MODELS_DIR, "trained_model.pkl"))

    with open(os.path.join(MODELS_DIR, "validation_results.json"), "w") as f:
        json.dump({"results": results, "best_model": best_name,
                   "train_seasons": TRAIN_SEASONS, "val_seasons": VAL_SEASONS, "test_seasons": TEST_SEASONS},
                  f, indent=2)

    print(f"\nSaved best model ({best_name}, refit on train+val) to models/trained_model.pkl")
    print("Test-set evaluation happens separately in evaluate_model.py (held out until now).")


if __name__ == "__main__":
    main()
