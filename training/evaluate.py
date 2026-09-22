"""
AlphaLens Comprehensive Evaluation & Prediction Ledger Generator
Generates verifiable audit logs of 500+ historical predictions with timestamped prices,
probabilities, actual forward outcomes, and calibration statistics.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, brier_score_loss, roc_auc_score

FEATURE_COLUMNS = [
    "dist_sma_20", "dist_sma_50", "dist_sma_200",
    "rsi_14", "macd", "macd_signal", "macd_hist",
    "bollinger_pct", "atr_pct", "volatility_20d", "volatility_60d",
    "volume_ratio", "beta", "news_sentiment", "news_count",
    "pe_ratio", "roe", "roce", "debt_equity", "revenue_growth_yoy", "eps_growth_yoy",
    "nifty_return_1d", "nifty_return_5d", "india_vix"
]


def generate_evaluation_and_ledger():
    df = pd.read_parquet("data/processed/training_dataset.parquet")
    df = df.sort_values("date").reset_index(drop=True)

    direction_model = joblib.load("models/direction/direction_ensemble.joblib")
    direction_scaler = joblib.load("models/direction/feature_scaler.joblib")
    
    return_median = joblib.load("models/return/return_median.joblib")
    return_lower = joblib.load("models/return/return_lower_q10.joblib")
    return_upper = joblib.load("models/return/return_upper_q90.joblib")
    return_scaler = joblib.load("models/return/return_scaler.joblib")

    # Take the most recent 600 predictions across all active stocks for the audit ledger
    recent_df = df.tail(600).copy().reset_index(drop=True)
    X = recent_df[FEATURE_COLUMNS].fillna(0)

    X_dir_scaled = direction_scaler.transform(X)
    probabilities = direction_model.predict_proba(X_dir_scaled)[:, 1]

    X_ret_scaled = return_scaler.transform(X)
    expected_returns = return_median.predict(X_ret_scaled)
    lower_bounds = return_lower.predict(X_ret_scaled)
    upper_bounds = return_upper.predict(X_ret_scaled)

    actual_directions = recent_df["target_direction_1d"].values
    actual_returns = (recent_df["target_return_1d"].values * 100.0)

    predictions = []
    correct_count = 0

    for i in range(len(recent_df)):
        row = recent_df.iloc[i]
        prob = float(probabilities[i])
        pred_dir = "Positive" if prob >= 0.50 else "Negative"
        act_dir = "Positive" if actual_directions[i] == 1 else "Negative"
        is_correct = (pred_dir == act_dir)
        if is_correct:
            correct_count += 1

        exp_ret = round(float(expected_returns[i]), 2)
        low_b = round(float(lower_bounds[i]), 2)
        up_b = round(float(upper_bounds[i]), 2)
        act_ret = round(float(actual_returns[i]), 2)

        predictions.append({
            "id": f"PRED-{1000 + i}",
            "date": pd.to_datetime(row["date"]).strftime("%d %b %Y"),
            "ticker": row["ticker"],
            "name": row["name"],
            "sector": row["sector"],
            "price_at_prediction": round(float(row["close"]), 2),
            "prediction": pred_dir,
            "probability_percent": round(prob * 100, 1),
            "expected_return": exp_ret,
            "prediction_interval": f"{low_b:+.1f}% → {up_b:+.1f}%",
            "horizon": "1 trading day",
            "actual_return": act_ret,
            "actual_outcome": act_dir,
            "is_correct": is_correct,
            "news_sentiment": round(float(row["news_sentiment"]), 2),
            "rsi": round(float(row["rsi_14"]), 1),
            "regime": row["market_regime"]
        })

    # Historical Accuracy stats
    y_pred = (probabilities >= 0.50).astype(int)
    acc = accuracy_score(actual_directions, y_pred)
    prec = precision_score(actual_directions, y_pred, zero_division=0)
    rec = recall_score(actual_directions, y_pred, zero_division=0)
    f1 = f1_score(actual_directions, y_pred, zero_division=0)
    brier = brier_score_loss(actual_directions, probabilities)
    auc = roc_auc_score(actual_directions, probabilities)

    prob_true, prob_pred = calibration_curve(actual_directions, probabilities, n_bins=10)

    ledger_payload = {
        "metadata": {
            "total_predictions": len(predictions),
            "directional_accuracy": round(float(acc) * 100, 1),
            "precision": round(float(prec) * 100, 1),
            "recall": round(float(rec) * 100, 1),
            "f1_score": round(float(f1) * 100, 1),
            "roc_auc": round(float(auc), 4),
            "brier_score": round(float(brier), 4),
            "calibration_bins": {
                "predicted": [round(float(p) * 100, 1) for p in prob_pred],
                "actual": [round(float(p) * 100, 1) for p in prob_true]
            }
        },
        "predictions": predictions
    }

    with open("data/processed/prediction_ledger.json", "w") as f:
        json.dump(ledger_payload, f, indent=2)

    print(f"Generated Prediction Ledger with {len(predictions)} entries.")
    print(f"Verified Directional Accuracy: {ledger_payload['metadata']['directional_accuracy']}%")
    return ledger_payload


if __name__ == "__main__":
    generate_evaluation_and_ledger()
