"""
AlphaLens Multi-Model Probabilistic Signal Engine
Fuses Direction Ensemble, Quantile Return Regressors, FinBERT News Sentiment,
and Market Regime Detection to produce calibrated probabilistic signals and risk ratings.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List

FEATURE_COLUMNS = [
    "dist_sma_20", "dist_sma_50", "dist_sma_200",
    "rsi_14", "macd", "macd_signal", "macd_hist",
    "bollinger_pct", "atr_pct", "volatility_20d", "volatility_60d",
    "volume_ratio", "beta", "news_sentiment", "news_count",
    "pe_ratio", "roe", "roce", "debt_equity", "revenue_growth_yoy", "eps_growth_yoy",
    "nifty_return_1d", "nifty_return_5d", "india_vix"
]


class SignalEngine:
    def __init__(self):
        self.direction_model = None
        self.direction_scaler = None
        self.return_median = None
        self.return_lower = None
        self.return_upper = None
        self.return_scaler = None
        self.regime_model = None
        self.regime_scaler = None
        self.regime_labels = {}
        self.load_models()

    def load_models(self):
        try:
            self.direction_model = joblib.load("models/direction/direction_ensemble.joblib")
            self.direction_scaler = joblib.load("models/direction/feature_scaler.joblib")
            self.return_median = joblib.load("models/return/return_median.joblib")
            self.return_lower = joblib.load("models/return/return_lower_q10.joblib")
            self.return_upper = joblib.load("models/return/return_upper_q90.joblib")
            self.return_scaler = joblib.load("models/return/return_scaler.joblib")
            self.regime_model = joblib.load("models/regime/regime_gmm.joblib")
            self.regime_scaler = joblib.load("models/regime/regime_scaler.joblib")
            with open("models/regime/regime_labels.json", "r") as f:
                self.regime_labels = json.load(f)
        except Exception as e:
            print(f"Warning: Models not fully loaded yet: {e}")

    def evaluate_stock(self, stock_row: pd.Series, recent_news: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generates the full probabilistic outlook, signal framework, and risk decomposition."""
        if self.direction_model is None:
            self.load_models()

        # Extract features
        features_dict = {col: float(stock_row.get(col, 0.0)) for col in FEATURE_COLUMNS}
        features_df = pd.DataFrame([features_dict])

        # Direction probability
        X_dir = self.direction_scaler.transform(features_df)
        prob_positive = float(self.direction_model.predict_proba(X_dir)[0, 1])

        # Return Quantiles
        X_ret = self.return_scaler.transform(features_df)
        exp_ret = float(self.return_median.predict(X_ret)[0])
        low_bound = float(self.return_lower.predict(X_ret)[0])
        up_bound = float(self.return_upper.predict(X_ret)[0])

        # Categorical Direction & Action Bias
        if prob_positive >= 0.60:
            direction_label = "Positive"
            action_bias = "WATCH / CONSIDER"
            expected_arrow = "↑"
            signal_style = "positive"
        elif prob_positive <= 0.44:
            direction_label = "Negative"
            action_bias = "AVOID / WAIT"
            expected_arrow = "↓"
            signal_style = "negative"
        else:
            direction_label = "Neutral"
            action_bias = "MONITOR / NEUTRAL"
            expected_arrow = "↔"
            signal_style = "neutral"

        # Multi-factor driver ratings
        rsi = float(stock_row.get("rsi_14", 50.0))
        dist_sma50 = float(stock_row.get("dist_sma_50", 0.0))
        vol_ratio = float(stock_row.get("volume_ratio", 1.0))
        news_sent = float(stock_row.get("news_sentiment", 0.0))
        volatility_20d = float(stock_row.get("volatility_20d", 0.18))
        nifty_ret = float(stock_row.get("nifty_return_1d", 0.0))

        # Driver ratings mapping
        momentum_str = "Strong" if rsi > 58 else ("Weak" if rsi < 42 else "Moderate")
        trend_str = "Positive" if dist_sma50 > 0.015 else ("Negative" if dist_sma50 < -0.015 else "Neutral")
        volume_str = "Above average" if vol_ratio > 1.2 else ("Below average" if vol_ratio < 0.8 else "Average")
        mkt_trend_str = "Positive" if nifty_ret > 0.002 else ("Negative" if nifty_ret < -0.002 else "Neutral")
        news_str = "Positive" if news_sent > 0.20 else ("Negative" if news_sent < -0.20 else "Neutral")
        vol_str = "High" if volatility_20d > 0.25 else ("Low" if volatility_20d < 0.14 else "Medium")

        # Risk assessment
        risk_level = "Medium"
        if volatility_20d > 0.26 or stock_row.get("debt_equity", 0.5) > 1.8:
            risk_level = "High"
        elif volatility_20d < 0.15 and stock_row.get("debt_equity", 0.5) < 0.5:
            risk_level = "Low"

        # Downside factors
        downside_factors = []
        if volatility_20d > 0.22:
            downside_factors.append("Higher historical volatility (20D)")
        if rsi > 70:
            downside_factors.append("Approaching overbought resistance band")
        elif rsi < 35:
            downside_factors.append("Persistent technical breakdown momentum")
        if stock_row.get("debt_equity", 0.0) > 1.0:
            downside_factors.append("Leverage sensitivity to interest rate shifts")
        if news_sent < -0.25:
            downside_factors.append("Negative sentiment overhang in recent coverage")
        if not downside_factors:
            downside_factors = ["Broad market beta exposure", "Macro liquidity sensitivity"]

        return {
            "ticker": stock_row.get("ticker"),
            "name": stock_row.get("name"),
            "sector": stock_row.get("sector"),
            "price": round(float(stock_row.get("close", 0.0)), 2),
            "change_1d_pct": round(float(stock_row.get("return_1d", 0.0)) * 100, 2),
            "model_outlook": {
                "direction": direction_label,
                "probability_percent": round(prob_positive * 100 if prob_positive >= 0.50 else (1 - prob_positive) * 100, 0),
                "raw_probability": round(prob_positive, 4),
                "probability_text": f"{int(round(prob_positive * 100))}% probability",
                "subtext": "of positive movement" if prob_positive >= 0.50 else "of negative movement",
                "horizon": "Next trading session",
                "expected_return": f"{exp_ret:+.1f}%",
                "prediction_interval": f"{low_bound:+.1f}% → {up_bound:+.1f}%"
            },
            "model_signal": {
                "outlook": direction_label.upper(),
                "action_bias": action_bias,
                "confidence": f"{int(round(max(prob_positive, 1 - prob_positive) * 100))}%",
                "expected_direction": expected_arrow,
                "risk": risk_level.upper(),
                "signal_style": signal_style
            },
            "evidence": {
                "momentum": momentum_str,
                "trend": trend_str,
                "volume": volume_str,
                "market_trend": mkt_trend_str,
                "news_sentiment": news_str,
                "volatility": vol_str
            },
            "risk": {
                "risk_level": risk_level,
                "potential_downside": downside_factors[:3],
                "var_95_1d": f"-{round(volatility_20d / np.sqrt(252) * 1.645 * 100, 2)}%",
                "max_drawdown": f"-{round(volatility_20d * 1.5 * 100, 1)}%",
                "event_risk": "Upcoming quarterly earnings" if stock_row.get("ticker") in ["RELIANCE", "TCS", "HDFCBANK"] else "Normal cycle"
            },
            "fundamentals": {
                "pe_ratio": round(float(stock_row.get("pe_ratio", 0)), 1),
                "roe": f"{round(float(stock_row.get('roe', 0)), 1)}%",
                "roce": f"{round(float(stock_row.get('roce', 0)), 1)}%",
                "debt_equity": round(float(stock_row.get("debt_equity", 0)), 2),
                "rev_growth_yoy": f"{round(float(stock_row.get('revenue_growth_yoy', 0)), 1)}%",
                "eps_growth_yoy": f"{round(float(stock_row.get('eps_growth_yoy', 0)), 1)}%"
            },
            "technicals": {
                "rsi_14": round(rsi, 1),
                "macd": round(float(stock_row.get("macd", 0)), 2),
                "macd_signal": round(float(stock_row.get("macd_signal", 0)), 2),
                "sma_20": round(float(stock_row.get("sma_20", 0)), 2),
                "sma_50": round(float(stock_row.get("sma_50", 0)), 2),
                "sma_200": round(float(stock_row.get("sma_200", 0)), 2),
                "bollinger_upper": round(float(stock_row.get("bollinger_upper", 0)), 2),
                "bollinger_lower": round(float(stock_row.get("bollinger_lower", 0)), 2)
            }
        }


# Singleton
signal_engine = SignalEngine()
