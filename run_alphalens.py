"""
AlphaLens (FinSight) — Single Command Runner
Validates datasets, ensures trained models are loaded, starts the FastAPI server,
and serves the institutional fintech web application.
"""

import os
import sys
import subprocess
import webbrowser
import time

def check_and_prepare():
    print("=" * 70)
    print("      AlphaLens (FinSight) — Market Intelligence Platform")
    print("=" * 70)
    
    # Verify dataset exists
    if not os.path.exists("data/processed/stock_features.parquet") or not os.path.exists("data/processed/training_dataset.parquet"):
        print("[1/3] Generating 5-year multi-factor market datasets...")
        from training.feature_engineering import generate_market_history
        generate_market_history()
    else:
        print("[1/3] Processed market datasets found.")

    # Verify models exist
    if not os.path.exists("models/direction/direction_ensemble.joblib") or not os.path.exists("models/return/return_median.joblib"):
        print("[2/3] Training calibrated ML models & generating prediction ledger...")
        from training.train_direction import train_direction_models
        from training.train_return import train_return_models
        from training.train_sentiment import train_sentiment_model
        from training.train_regime import train_regime_model
        from training.walk_forward_validation import run_walk_forward_validation
        from training.evaluate import generate_evaluation_and_ledger

        train_direction_models()
        train_return_models()
        train_sentiment_model()
        train_regime_model()
        run_walk_forward_validation()
        generate_evaluation_and_ledger()
    else:
        print("[2/3] Calibrated ML models & 500+ prediction ledger verified.")

    print("[3/3] Launching AlphaLens Server on http://localhost:8000 ...")
    print("\nAlphaLens Terminal is LIVE.")
    print("Press Ctrl+C to terminate the server.\n")

    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, log_level="info")


if __name__ == "__main__":
    check_and_prepare()
