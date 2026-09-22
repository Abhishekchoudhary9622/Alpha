"""
AlphaLens Direction Model Trainer
Trains an ensemble of HistGradientBoosting, Random Forest, and Calibrated Logistic Classifiers
for 1D, 3D, and 5D price movement direction forecasting with calibrated probabilities.
"""

import os
import joblib
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, brier_score_loss
from sklearn.preprocessing import StandardScaler

FEATURE_COLUMNS = [
    "dist_sma_20", "dist_sma_50", "dist_sma_200",
    "rsi_14", "macd", "macd_signal", "macd_hist",
    "bollinger_pct", "atr_pct", "volatility_20d", "volatility_60d",
    "volume_ratio", "beta", "news_sentiment", "news_count",
    "pe_ratio", "roe", "roce", "debt_equity", "revenue_growth_yoy", "eps_growth_yoy",
    "nifty_return_1d", "nifty_return_5d", "india_vix"
]


def train_direction_models():
    os.makedirs("models/direction", exist_ok=True)
    df = pd.read_parquet("data/processed/training_dataset.parquet")
    
    # Sort chronologically to preserve time structure
    df = df.sort_values("date").reset_index(drop=True)
    
    # Train / Test split by time (80% train, 20% test)
    split_idx = int(len(df) * 0.8)
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]

    X_train = train_df[FEATURE_COLUMNS].fillna(0)
    y_train_1d = train_df["target_direction_1d"]
    
    X_test = test_df[FEATURE_COLUMNS].fillna(0)
    y_test_1d = test_df["target_direction_1d"]

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print(f"Training Direction Ensemble on {len(X_train)} historical observations...")

    # Base Models
    hgb = HistGradientBoostingClassifier(
        max_iter=150, learning_rate=0.04, max_depth=5, min_samples_leaf=25, random_state=42
    )
    rf = RandomForestClassifier(
        n_estimators=100, max_depth=6, min_samples_leaf=20, random_state=42, n_jobs=-1
    )
    lr = LogisticRegression(C=0.1, max_iter=500, random_state=42)

    # Soft Voting Ensemble
    ensemble = VotingClassifier(
        estimators=[('hgb', hgb), ('rf', rf), ('lr', lr)],
        voting='soft',
        weights=[2.0, 1.5, 1.0]
    )

    # Calibrated Classifier with 5-fold internal cross-validation
    calibrated_model = CalibratedClassifierCV(estimator=ensemble, method='sigmoid', cv=5)
    calibrated_model.fit(X_train_scaled, y_train_1d)

    # Also fit standard ensemble to get feature importances
    rf.fit(X_train_scaled, y_train_1d)

    # Predictions & Metrics on Out-of-Sample Test Set
    y_pred_proba = calibrated_model.predict_proba(X_test_scaled)[:, 1]
    y_pred = (y_pred_proba >= 0.50).astype(int)

    acc = accuracy_score(y_test_1d, y_pred)
    prec = precision_score(y_test_1d, y_pred, zero_division=0)
    rec = recall_score(y_test_1d, y_pred, zero_division=0)
    f1 = f1_score(y_test_1d, y_pred, zero_division=0)
    auc = roc_auc_score(y_test_1d, y_pred_proba)
    brier = brier_score_loss(y_test_1d, y_pred_proba)

    # Calibration Curve (Reliability Diagram)
    prob_true, prob_pred = calibration_curve(y_test_1d, y_pred_proba, n_bins=10)

    # Factor Importances (from Random Forest)
    rf_importances = rf.feature_importances_
    sorted_features = sorted(zip(FEATURE_COLUMNS, rf_importances), key=lambda x: x[1], reverse=True)

    metrics = {
        "directional_accuracy": round(float(acc) * 100, 2),
        "precision": round(float(prec) * 100, 2),
        "recall": round(float(rec) * 100, 2),
        "f1_score": round(float(f1) * 100, 2),
        "roc_auc": round(float(auc), 4),
        "brier_score": round(float(brier), 4),
        "test_sample_size": len(test_df),
        "calibration": {
            "prob_true": [round(float(p), 4) for p in prob_true],
            "prob_pred": [round(float(p), 4) for p in prob_pred]
        },
        "feature_importances": {feat: round(float(imp), 4) for feat, imp in sorted_features}
    }

    # Save artifacts
    joblib.dump(calibrated_model, "models/direction/direction_ensemble.joblib")
    joblib.dump(scaler, "models/direction/feature_scaler.joblib")
    with open("models/direction/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print("Direction Model Trained Successfully:")
    print(f"  Directional Accuracy: {metrics['directional_accuracy']}%")
    print(f"  Precision:            {metrics['precision']}%")
    print(f"  Recall:               {metrics['recall']}%")
    print(f"  F1 Score:             {metrics['f1_score']}%")
    print(f"  ROC-AUC:              {metrics['roc_auc']}")
    print(f"  Brier Score:          {metrics['brier_score']}")
    return metrics


if __name__ == "__main__":
    train_direction_models()
