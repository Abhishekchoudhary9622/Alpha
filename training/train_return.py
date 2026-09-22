"""
AlphaLens Return Quantile Regression Model Trainer
Trains Gradient Boosting Quantile Regressors (alpha=0.10, 0.50, 0.90) to generate
expected forward return point forecasts along with probabilistic prediction intervals.
"""

import os
import joblib
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler

FEATURE_COLUMNS = [
    "dist_sma_20", "dist_sma_50", "dist_sma_200",
    "rsi_14", "macd", "macd_signal", "macd_hist",
    "bollinger_pct", "atr_pct", "volatility_20d", "volatility_60d",
    "volume_ratio", "beta", "news_sentiment", "news_count",
    "pe_ratio", "roe", "roce", "debt_equity", "revenue_growth_yoy", "eps_growth_yoy",
    "nifty_return_1d", "nifty_return_5d", "india_vix"
]


def train_return_models():
    os.makedirs("models/return", exist_ok=True)
    df = pd.read_parquet("data/processed/training_dataset.parquet")
    df = df.sort_values("date").reset_index(drop=True)

    split_idx = int(len(df) * 0.8)
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]

    X_train = train_df[FEATURE_COLUMNS].fillna(0)
    y_train = train_df["target_return_1d"] * 100.0  # In percentage points

    X_test = test_df[FEATURE_COLUMNS].fillna(0)
    y_test = test_df["target_return_1d"] * 100.0

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print(f"Training Quantile Return Regressors (10th, 50th, 90th percentiles)...")

    # Median / Expected Return Model (50th percentile / Least Absolute Deviations)
    median_reg = HistGradientBoostingRegressor(
        loss="quantile", quantile=0.50, max_iter=120, learning_rate=0.03, random_state=42
    )
    median_reg.fit(X_train_scaled, y_train)

    # Lower Bound Model (10th percentile)
    lower_reg = HistGradientBoostingRegressor(
        loss="quantile", quantile=0.10, max_iter=120, learning_rate=0.03, random_state=42
    )
    lower_reg.fit(X_train_scaled, y_train)

    # Upper Bound Model (90th percentile)
    upper_reg = HistGradientBoostingRegressor(
        loss="quantile", quantile=0.90, max_iter=120, learning_rate=0.03, random_state=42
    )
    upper_reg.fit(X_train_scaled, y_train)

    # Predictions & Metrics
    pred_median = median_reg.predict(X_test_scaled)
    pred_lower = lower_reg.predict(X_test_scaled)
    pred_upper = upper_reg.predict(X_test_scaled)

    mae = mean_absolute_error(y_test, pred_median)
    rmse = np.sqrt(mean_squared_error(y_test, pred_median))
    interval_coverage = np.mean((y_test >= pred_lower) & (y_test <= pred_upper)) * 100.0

    metrics = {
        "mae_percent": round(float(mae), 3),
        "rmse_percent": round(float(rmse), 3),
        "interval_80pct_coverage": round(float(interval_coverage), 2),
        "avg_interval_width": round(float(np.mean(pred_upper - pred_lower)), 3),
        "test_samples": len(test_df)
    }

    # Save models
    joblib.dump(median_reg, "models/return/return_median.joblib")
    joblib.dump(lower_reg, "models/return/return_lower_q10.joblib")
    joblib.dump(upper_reg, "models/return/return_upper_q90.joblib")
    joblib.dump(scaler, "models/return/return_scaler.joblib")

    with open("models/return/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print("Return Models Trained Successfully:")
    print(f"  MAE:                       ±{metrics['mae_percent']}%")
    print(f"  80% Interval Empirical Coverage: {metrics['interval_80pct_coverage']}%")
    print(f"  Average Interval Width:    {metrics['avg_interval_width']}%")
    return metrics


if __name__ == "__main__":
    train_return_models()
