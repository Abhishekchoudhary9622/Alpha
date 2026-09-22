"""
AlphaLens Financial News Sentiment & Impact Model
FinBERT-inspired financial domain sentiment classifier and event impact weight estimator.
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
import joblib

FINANCIAL_LEXICON = {
    "growth": 0.65, "beat": 0.85, "surge": 0.80, "rally": 0.75, "upgrade": 0.70,
    "expansion": 0.60, "record": 0.70, "profit": 0.65, "dividend": 0.55, "buyback": 0.80,
    "robust": 0.70, "outperform": 0.75, "strong": 0.65, "bullish": 0.75, "contract": 0.70,
    "decline": -0.65, "miss": -0.80, "fall": -0.70, "slump": -0.75, "downgrade": -0.75,
    "scrutiny": -0.70, "investigation": -0.85, "loss": -0.75, "inflation": -0.55,
    "headwind": -0.60, "disruption": -0.65, "weak": -0.65, "bearish": -0.75, "risk": -0.50
}


def train_sentiment_model():
    os.makedirs("models/sentiment", exist_ok=True)
    news_df = pd.read_parquet("data/processed/news_features.parquet")

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=1000)
    X = vectorizer.fit_transform(news_df["headline"])
    y = news_df["finbert_sentiment"]

    reg = Ridge(alpha=1.0)
    reg.fit(X, y)

    joblib.dump(vectorizer, "models/sentiment/tfidf_vectorizer.joblib")
    joblib.dump(reg, "models/sentiment/sentiment_regressor.joblib")

    with open("models/sentiment/lexicon.json", "w") as f:
        json.dump(FINANCIAL_LEXICON, f, indent=2)

    print(f"FinBERT News Sentiment Model fitted on {len(news_df)} headlines.")
    return {"trained_samples": len(news_df)}


if __name__ == "__main__":
    train_sentiment_model()
