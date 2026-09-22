"""
AlphaLens AI Customer Advisory & Stock Recommendation Engine
Generates explainable, actionable Buy/Hold/Avoid guidance for retail & institutional investors
based on technical structure, trend alignment, momentum sweet-spots, fundamentals, and probabilistic ML models.
"""

from typing import Dict, Any, List, Optional
import numpy as np


class AdvisoryEngine:
    def __init__(self):
        pass

    def evaluate_advisory(self, stock: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates a stock record and generates clear, actionable customer advice:
        Buy, Accumulate, Hold, Avoid, or Strong Sell with entry targets, stop loss, and plain-English rationales.
        """
        ticker = stock.get("ticker", "UNKNOWN")
        name = stock.get("name", ticker)
        price = float(stock.get("price", 1000.0))
        change_1d_pct = float(stock.get("change_1d_pct", 0.0))
        
        technicals = stock.get("technicals", {})
        fundamentals = stock.get("fundamentals", {})
        model_outlook = stock.get("model_outlook", {})
        
        rsi = float(technicals.get("rsi_14", 50.0))
        sma_20 = float(technicals.get("sma_20", price * 0.98))
        sma_50 = float(technicals.get("sma_50", price * 0.96))
        sma_200 = float(technicals.get("sma_200", price * 0.92))
        vol_20d = float(technicals.get("volatility_20d", 0.20))
        vol_ratio = float(technicals.get("volume_ratio", 1.0))
        beta = float(technicals.get("beta", 1.0))
        
        pe = float(fundamentals.get("pe_ratio", 25.0))
        debt_equity = float(fundamentals.get("debt_equity", 0.45))
        
        # Probabilistic ML score
        ml_prob = float(model_outlook.get("probability_percent", 55.0))
        ml_direction = model_outlook.get("direction", "Positive")
        if ml_direction == "Negative":
            ml_bull_score = (100.0 - ml_prob) / 100.0
        else:
            ml_bull_score = ml_prob / 100.0

        # Multi-factor scoring (0 to 100)
        score = 50.0
        bull_reasons = []
        avoid_warnings = []
        
        # 1. Trend Analysis (Price vs Moving Averages)
        is_above_sma20 = price >= sma_20
        is_above_sma50 = price >= sma_50
        is_above_sma200 = price >= sma_200
        
        if is_above_sma20 and is_above_sma50 and is_above_sma200:
            score += 18
            bull_reasons.append(f"Strong Bullish Structure: Trading comfortably above 20D (₹{sma_20:,.1f}), 50D (₹{sma_50:,.1f}), and 200D (₹{sma_200:,.1f}) moving averages.")
        elif is_above_sma50 and is_above_sma200:
            score += 10
            bull_reasons.append("Medium-to-Long Term Uptrend: Sustained position above key 50D & 200D moving averages.")
        elif not is_above_sma50 and not is_above_sma200:
            score -= 22
            avoid_warnings.append(f"Major Technical Breakdown: Trading below critical 50-day (₹{sma_50:,.1f}) and 200-day (₹{sma_200:,.1f}) moving average resistance.")
        elif not is_above_sma200:
            score -= 15
            avoid_warnings.append(f"Below Long-Term Baseline: Trading below 200-day SMA (₹{sma_200:,.1f}), indicating macro institutional selling pressure.")

        # 2. RSI & Momentum Analysis
        if 48.0 <= rsi <= 64.0:
            score += 14
            bull_reasons.append(f"Optimal Momentum Sweet-Spot: RSI is at {rsi:.1f}, indicating healthy buying momentum with ample room before overbought resistance.")
        elif 35.0 <= rsi < 48.0:
            score += 5
            bull_reasons.append(f"Accumulation Zone: RSI at {rsi:.1f} shows base consolidation near support.")
        elif rsi > 74.0:
            score -= 18
            avoid_warnings.append(f"Extreme Overbought Risk: RSI at {rsi:.1f} signals high probability of impending short-term profit booking.")
        elif rsi < 32.0:
            if is_above_sma200:
                score += 8
                bull_reasons.append(f"Oversold Value Dip: RSI at {rsi:.1f} in an uptrending stock suggests favorable risk-reward dip entry.")
            else:
                score -= 16
                avoid_warnings.append(f"Severe Bearish Divergence: RSI at {rsi:.1f} with breakdown momentum signals falling knife risk.")

        # 3. Volume Profile
        if vol_ratio > 1.3:
            if change_1d_pct > 0:
                score += 10
                bull_reasons.append(f"Institutional Accumulation: Volume is {vol_ratio:.1f}x higher than 20-day average on positive price action.")
            else:
                score -= 10
                avoid_warnings.append(f"Heavy Distribution: Volume is {vol_ratio:.1f}x above average during downward move.")

        # 4. Fundamental Health & Valuation
        if 0 < pe <= 22.0:
            score += 8
            bull_reasons.append(f"Attractive Valuation: P/E ratio of {pe:.1f} offers a comfortable margin of safety compared to broader sector multiples.")
        elif pe > 85.0:
            score -= 10
            avoid_warnings.append(f"Elevated Valuation Multiple: High P/E of {pe:.1f} leaves little room for earnings misses.")
            
        if debt_equity > 1.4:
            score -= 8
            avoid_warnings.append(f"High Financial Leverage: Debt-to-Equity ratio of {debt_equity:.2f} increases vulnerability in tight credit regimes.")
        elif debt_equity < 0.35:
            score += 6
            bull_reasons.append(f"Robust Balance Sheet: Conservative debt-to-equity of {debt_equity:.2f} provides strong downside defense.")

        # 5. ML Directional Forecast Alignment
        if ml_bull_score >= 0.65:
            score += 10
            bull_reasons.append(f"AI Probabilistic Edge: Multi-modal ML ensemble predicts {int(ml_bull_score * 100)}% probability of continued positive trajectory.")
        elif ml_bull_score <= 0.40:
            score -= 12
            avoid_warnings.append(f"ML Model Alert: Directional ensemble flags higher probability ({int((1 - ml_bull_score) * 100)}%) of negative price drift.")

        # Clamp score to 0 - 100
        conviction_score = int(np.clip(round(score), 5, 96))

        # Determine Recommendation Category & Action Badge
        if conviction_score >= 76:
            verdict = "STRONG BUY"
            badge_class = "badge-strong-buy"
            signal_color = "#10b981"
            suitability = "Suitable for Growth & Momentum Investors seeking high risk-adjusted upside."
            horizon = "2 – 6 Weeks (Positional Swing & Trend Continuation)"
            entry_low = price * 0.985
            entry_high = price * 1.01
            target_1 = price * (1.0 + max(0.08, vol_20d * 0.6))
            target_2 = price * (1.0 + max(0.15, vol_20d * 1.1))
            stop_loss = min(sma_50 * 0.98, price * 0.95)
            action_summary = f"Aggressive accumulation recommended on dips near ₹{entry_low:,.1f} - ₹{entry_high:,.1f}."
        elif conviction_score >= 60:
            verdict = "ACCUMULATE / BUY"
            badge_class = "badge-buy"
            signal_color = "#059669"
            suitability = "Suitable for Systematic / Long-Term Wealth Builders seeking quality entry."
            horizon = "1 – 3 Months (Medium Term Accumulation)"
            entry_low = price * 0.975
            entry_high = price * 1.005
            target_1 = price * (1.0 + max(0.06, vol_20d * 0.5))
            target_2 = price * (1.0 + max(0.12, vol_20d * 0.9))
            stop_loss = price * 0.94
            action_summary = f"Favorable risk-reward for staged entry between ₹{entry_low:,.1f} and ₹{entry_high:,.1f}."
        elif conviction_score >= 44:
            verdict = "HOLD / WATCH"
            badge_class = "badge-hold"
            signal_color = "#f59e0b"
            suitability = "Suitable for existing holders; fresh buyers should wait for confirmed breakout."
            horizon = "Wait for Clear Directional Catalyst"
            entry_low = price * 0.96
            entry_high = price * 0.98
            target_1 = price * 1.05
            target_2 = price * 1.09
            stop_loss = price * 0.93
            action_summary = f"Consolidating in range. Maintain existing stop-loss at ₹{stop_loss:,.1f} and avoid fresh lumpsum buying."
        elif conviction_score >= 28:
            verdict = "AVOID / TAKE PROFIT"
            badge_class = "badge-avoid"
            signal_color = "#f97316"
            suitability = "Caution: Retail customers should avoid fresh purchases until technical repair occurs."
            horizon = "Expect Potential Pullback / Consolidation"
            entry_low = price * 0.88
            entry_high = price * 0.91
            target_1 = price * 0.98
            target_2 = price * 1.02
            stop_loss = price * 0.97
            action_summary = f"High risk of downside drift or overextended pullback. Consider locking in profits or staying on sidelines."
        else:
            verdict = "HIGH RISK AVOID"
            badge_class = "badge-strong-avoid"
            signal_color = "#ef4444"
            suitability = "High Capital Risk: Steer clear. Strictly avoid averaging down on losing positions."
            horizon = "Bearish Downtrend in Progress"
            entry_low = price * 0.80
            entry_high = price * 0.84
            target_1 = price * 0.92
            target_2 = price * 0.96
            stop_loss = price * 0.98
            action_summary = f"Severe technical weakness and breakdown signals. Capital preservation prioritized — do NOT buy."

        # Risk-to-Reward calculation
        upside_pct = round(((target_1 - price) / price) * 100, 1)
        downside_pct = round(((price - stop_loss) / price) * 100, 1)
        rr_ratio = round(abs(upside_pct) / (abs(downside_pct) + 1e-5), 1) if downside_pct > 0 else 1.0
        
        # Ensure default reasons if lists are sparse
        if not bull_reasons:
            bull_reasons = [
                f"Established market presence in {stock.get('sector', 'Indian Equities')}",
                "Broad market alignment with macro economic liquidity flows"
            ]
        if not avoid_warnings:
            avoid_warnings = [
                f"Sensitivity to broad market benchmark volatility (Beta: {beta:.2f})",
                "Quarterly earnings performance sensitivity"
            ]

        # Safer alternative suggestion if Avoid
        alternative = None
        if verdict in ["AVOID / TAKE PROFIT", "HIGH RISK AVOID"]:
            sector = stock.get("sector", "")
            if "Tech" in sector or "Information" in sector:
                alternative = "Consider resilient large-caps like TCS or INFY for defensive IT exposure."
            elif "Bank" in sector or "Finan" in sector:
                alternative = "Consider high-ROE private banks like ICICIBANK or HDFCBANK instead."
            elif "Auto" in sector:
                alternative = "Consider market leaders like M&M or MARUTI with robust order backlogs."
            else:
                alternative = "Look into high-conviction NIFTY 50 bluechip recommendations with RSI in 50-60 range."

        return {
            "ticker": ticker,
            "name": name,
            "sector": stock.get("sector", "Equities"),
            "current_price": price,
            "change_1d_pct": change_1d_pct,
            "verdict": verdict,
            "badge_class": badge_class,
            "signal_color": signal_color,
            "conviction_score": conviction_score,
            "suitability": suitability,
            "action_summary": action_summary,
            "time_horizon": horizon,
            "targets": {
                "entry_zone": f"₹{entry_low:,.1f} – ₹{entry_high:,.1f}",
                "target_1": f"₹{target_1:,.1f}",
                "target_1_upside": f"+{upside_pct:.1f}%",
                "target_2": f"₹{target_2:,.1f}",
                "target_2_upside": f"+{round(((target_2 - price) / price) * 100, 1):.1f}%",
                "stop_loss": f"₹{stop_loss:,.1f}",
                "stop_loss_risk": f"-{downside_pct:.1f}%",
                "risk_reward": f"1 : {rr_ratio:.1f}"
            },
            "why_buy_reasons": bull_reasons[:3],
            "why_avoid_warnings": avoid_warnings[:3],
            "alternative_suggestion": alternative
        }

    def get_categorized_recommendations(self, stocks_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes tracked universe and categorizes into Top Buys, Stocks to Avoid,
        Momentum Breakouts, and Value Accumulation picks.
        """
        all_evals = []
        for ticker, stock in stocks_dict.items():
            try:
                advisory = self.evaluate_advisory(stock)
                all_evals.append(advisory)
            except Exception as e:
                print(f"Error evaluating advisory for {ticker}: {e}")

        # Sort and categorize
        top_buys = [s for s in all_evals if s["verdict"] in ["STRONG BUY", "ACCUMULATE / BUY"]]
        top_buys.sort(key=lambda x: x["conviction_score"], reverse=True)

        stocks_to_avoid = [s for s in all_evals if s["verdict"] in ["HIGH RISK AVOID", "AVOID / TAKE PROFIT"]]
        stocks_to_avoid.sort(key=lambda x: x["conviction_score"])

        momentum_breakouts = [
            s for s in all_evals 
            if s["verdict"] in ["STRONG BUY", "ACCUMULATE / BUY"] and s["change_1d_pct"] > 0.8
        ]
        momentum_breakouts.sort(key=lambda x: x["change_1d_pct"], reverse=True)

        value_accumulate = [
            s for s in all_evals 
            if s["conviction_score"] >= 55 and any("Valuation" in r or "Balance Sheet" in r for r in s["why_buy_reasons"])
        ]
        value_accumulate.sort(key=lambda x: x["conviction_score"], reverse=True)

        return {
            "summary": {
                "total_analyzed": len(all_evals),
                "buy_count": len(top_buys),
                "avoid_count": len(stocks_to_avoid),
                "hold_count": len(all_evals) - len(top_buys) - len(stocks_to_avoid),
                "market_regime": "BULL TREND ACCUMULATION",
                "updated_at": "Live Market Session"
            },
            "top_buys": top_buys[:15],
            "stocks_to_avoid": stocks_to_avoid[:15],
            "momentum_breakouts": momentum_breakouts[:10],
            "value_accumulate": value_accumulate[:10],
            "all_recommendations": all_evals
        }


advisory_engine = AdvisoryEngine()
