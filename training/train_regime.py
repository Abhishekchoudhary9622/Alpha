"""
AlphaLens Market Regime Classifier
Identifies macroeconomic market states: BULL_TREND, BEAR_TREND, HIGH_VOLATILITY, RANGEBOUND.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler


def train_regime_model():
    os.makedirs("models/regime", exist_ok=True)
    df = pd.read_parquet("data/processed/training_dataset.parquet")

    # Aggregate to daily macro level
    daily_macro = df.groupby("date").agg({
        "nifty_return_1d": "mean",
        "nifty_return_5d": "mean",
        "india_vix": "mean"
    }).reset_index()

    features = ["nifty_return_1d", "nifty_return_5d", "india_vix"]
    X = daily_macro[features].fillna(0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    gmm = GaussianMixture(n_components=4, covariance_type="full", random_state=42)
    gmm.fit(X_scaled)

    joblib.dump(gmm, "models/regime/regime_gmm.joblib")
    joblib.dump(scaler, "models/regime/regime_scaler.joblib")

    regime_labels = {
        0: "BULL_TREND",
        1: "BEAR_TREND",
        2: "HIGH_VOLATILITY",
        3: "RANGEBOUND"
    }

    with open("models/regime/regime_labels.json", "w") as f:
        json.dump(regime_labels, f, indent=2)

    print(f"Market Regime Model fitted on {len(daily_macro)} daily macroeconomic states.")
    return {"macro_days": len(daily_macro)}


if __name__ == "__main__":
    train_regime_model()
