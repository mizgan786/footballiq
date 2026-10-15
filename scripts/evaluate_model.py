"""
evaluate_model.py

Final, one-time evaluation on the held-out test set (seasons 2023-2025),
which train_model.py never touched during training or model selection.

Produces:
  - Console metrics: MAE, RMSE, R2, MAPE (in euros)
  - reports/actual_vs_predicted.png
  - reports/residual_plot.png
  - reports/feature_importance.png
  - reports/error_distribution.png
  - models/test_results.json
"""

import os
import json
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")

TEST_SEASONS = [2023, 2024, 2025]


def main():
    os.makedirs(REPORTS_DIR, exist_ok=True)

    bundle = joblib.load(os.path.join(MODELS_DIR, "trained_model.pkl"))
    pipe, feature_cols, model_name = bundle["pipeline"], bundle["feature_columns"], bundle["model_name"]

    df = pd.read_csv(os.path.join(DATA_DIR, "model_features.csv"))
    test = df[df["season"].isin(TEST_SEASONS)].copy()
    X_test = test[feature_cols]
    y_test_log = test["log_market_value"].values

    pred_log = pipe.predict(X_test)
    y_true = np.exp(y_test_log)
    y_pred = np.exp(pred_log)

    metrics = {
        "model": model_name,
        "n_test_rows": len(test),
        "MAE_eur": float(mean_absolute_error(y_true, y_pred)),
        "RMSE_eur": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "R2": float(r2_score(y_true, y_pred)),
        "MAPE": float(mean_absolute_percentage_error(y_true, y_pred)),
    }
    print(f"Final test-set evaluation ({model_name}, seasons {TEST_SEASONS}, n={len(test):,}):")
    for k, v in metrics.items():
        if k in ("model", "n_test_rows"):
            continue
        print(f"  {k}: {v:,.4f}" if k == "R2" or k == "MAPE" else f"  {k}: \u20ac{v:,.0f}")

    with open(os.path.join(MODELS_DIR, "test_results.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    # --- Actual vs Predicted ---
    plt.figure(figsize=(6, 6))
    plt.scatter(y_true / 1e6, y_pred / 1e6, alpha=0.25, s=12)
    max_val = max(y_true.max(), y_pred.max()) / 1e6
    plt.plot([0, max_val], [0, max_val], "r--", linewidth=1)
    plt.xlabel("Actual Market Value (\u20acM)")
    plt.ylabel("Predicted Market Value (\u20acM)")
    plt.title(f"Actual vs Predicted ({model_name}, test set)")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "actual_vs_predicted.png"), dpi=120)
    plt.close()

    # --- Residual plot ---
    residuals = (y_pred - y_true) / 1e6
    plt.figure(figsize=(6, 4))
    plt.scatter(y_true / 1e6, residuals, alpha=0.25, s=12)
    plt.axhline(0, color="r", linestyle="--", linewidth=1)
    plt.xlabel("Actual Market Value (\u20acM)")
    plt.ylabel("Residual, Predicted - Actual (\u20acM)")
    plt.title("Residual Plot (test set)")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "residual_plot.png"), dpi=120)
    plt.close()

    # --- Feature importance ---
    model = pipe.named_steps["model"]
    if hasattr(model, "feature_importances_"):
        importances = pd.Series(model.feature_importances_, index=feature_cols).sort_values(ascending=False).head(15)
        plt.figure(figsize=(7, 6))
        importances.iloc[::-1].plot(kind="barh")
        plt.title(f"Top 15 Feature Importances ({model_name})")
        plt.tight_layout()
        plt.savefig(os.path.join(REPORTS_DIR, "feature_importance.png"), dpi=120)
        plt.close()
        importances.to_json(os.path.join(MODELS_DIR, "feature_importance.json"))

    # --- Prediction error distribution ---
    pct_error = (y_pred - y_true) / y_true * 100
    plt.figure(figsize=(6, 4))
    plt.hist(pct_error.clip(-100, 200), bins=40)
    plt.axvline(0, color="r", linestyle="--", linewidth=1)
    plt.xlabel("Prediction Error (%)")
    plt.ylabel("Count")
    plt.title("Prediction Error Distribution (test set)")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "error_distribution.png"), dpi=120)
    plt.close()

    print(f"\nSaved 4 diagnostic plots to {REPORTS_DIR}/")


if __name__ == "__main__":
    main()
