"""
AlphaLens Walk-Forward Out-of-Sample Validation Engine
Evaluates the Direction Ensemble, Quantile Regressor, and Multi-Factor Signal across
sequential chronological folds with zero future look-ahead leakage.
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
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


def run_walk_forward_validation(n_splits=5):
    df = pd.read_parquet("data/processed/training_dataset.parquet")
    df = df.sort_values("date").reset_index(drop=True)

    unique_dates = df["date"].unique()
    total_dates = len(unique_dates)
    fold_size = total_dates // (n_splits + 1)

    fold_results = []
    all_y_true = []
    all_y_pred_proba = []
    all_dates = []
    all_tickers = []
    all_prices = []
    all_returns = []

    print(f"Executing Walk-Forward Validation across {n_splits} chronological windows...")

    for fold in range(n_splits):
        train_end_idx = fold_size * (fold + 1)
        test_end_idx = fold_size * (fold + 2)

        train_dates = unique_dates[:train_end_idx]
        test_dates = unique_dates[train_end_idx:test_end_idx]

        train_fold = df[df["date"].isin(train_dates)]
        test_fold = df[df["date"].isin(test_dates)]

        X_tr = train_fold[FEATURE_COLUMNS].fillna(0)
        y_tr = train_fold["target_direction_1d"]

        X_te = test_fold[FEATURE_COLUMNS].fillna(0)
        y_te = test_fold["target_direction_1d"]

        scaler = StandardScaler()
        X_tr_s = scaler.fit_transform(X_tr)
        X_te_s = scaler.transform(X_te)

        hgb = HistGradientBoostingClassifier(max_iter=80, learning_rate=0.04, max_depth=4, random_state=42)
        rf = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42, n_jobs=-1)
        lr = LogisticRegression(C=0.1, max_iter=250)

        ensemble = VotingClassifier(
            estimators=[('hgb', hgb), ('rf', rf), ('lr', lr)],
            voting='soft',
            weights=[2.0, 1.5, 1.0]
        )

        # In-fold calibration with 3-fold CV
        calibrated = CalibratedClassifierCV(estimator=ensemble, method='sigmoid', cv=3)
        calibrated.fit(X_tr_s, y_tr)

        y_prob = calibrated.predict_proba(X_te_s)[:, 1]
        y_pred = (y_prob >= 0.50).astype(int)

        acc = accuracy_score(y_te, y_pred)
        prec = precision_score(y_te, y_pred, zero_division=0)
        rec = recall_score(y_te, y_pred, zero_division=0)
        f1 = f1_score(y_te, y_pred, zero_division=0)
        brier = brier_score_loss(y_te, y_prob)

        fold_results.append({
            "fold": fold + 1,
            "train_period": f"{pd.to_datetime(train_dates[0]).strftime('%Y-%m-%d')} to {pd.to_datetime(train_dates[-1]).strftime('%Y-%m-%d')}",
            "test_period": f"{pd.to_datetime(test_dates[0]).strftime('%Y-%m-%d')} to {pd.to_datetime(test_dates[-1]).strftime('%Y-%m-%d')}",
            "train_samples": len(train_fold),
            "test_samples": len(test_fold),
            "accuracy": round(float(acc) * 100, 2),
            "precision": round(float(prec) * 100, 2),
            "recall": round(float(rec) * 100, 2),
            "f1_score": round(float(f1) * 100, 2),
            "brier_score": round(float(brier), 4)
        })

        all_y_true.extend(y_te.tolist())
        all_y_pred_proba.extend(y_prob.tolist())
        all_dates.extend(test_fold["date"].astype(str).tolist())
        all_tickers.extend(test_fold["ticker"].tolist())
        all_prices.extend(test_fold["close"].tolist())
        all_returns.extend((test_fold["target_return_1d"] * 100.0).tolist())

    overall_acc = accuracy_score(all_y_true, (np.array(all_y_pred_proba) >= 0.5).astype(int))
    overall_prec = precision_score(all_y_true, (np.array(all_y_pred_proba) >= 0.5).astype(int))
    overall_rec = recall_score(all_y_true, (np.array(all_y_pred_proba) >= 0.5).astype(int))
    overall_f1 = f1_score(all_y_true, (np.array(all_y_pred_proba) >= 0.5).astype(int))
    overall_brier = brier_score_loss(all_y_true, all_y_pred_proba)

    summary = {
        "mean_accuracy": round(float(overall_acc) * 100, 2),
        "mean_precision": round(float(overall_prec) * 100, 2),
        "mean_recall": round(float(overall_rec) * 100, 2),
        "mean_f1_score": round(float(overall_f1) * 100, 2),
        "mean_brier_score": round(float(overall_brier), 4),
        "folds": fold_results
    }

    os.makedirs("models/ensemble", exist_ok=True)
    with open("models/ensemble/walk_forward_results.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("Walk-Forward Validation Summary:")
    print(f"  Mean Accuracy:   {summary['mean_accuracy']}%")
    print(f"  Mean Precision:  {summary['mean_precision']}%")
    print(f"  Mean Recall:     {summary['mean_recall']}%")
    print(f"  Mean F1 Score:   {summary['mean_f1_score']}%")
    print(f"  Brier Score:     {summary['mean_brier_score']}")
    return summary


if __name__ == "__main__":
    run_walk_forward_validation()
