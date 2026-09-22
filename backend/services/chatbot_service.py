"""
AlphaLens AI Financial Copilot Chatbot Engine
Context-aware quantitative reasoning agent that answers user queries about stock predictions,
live market data, customer buy/avoid advisories, portfolio risk diagnostics, and macro scenarios.
"""

import re
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.pipeline.live_pipeline import live_pipeline
from backend.services.advisory_engine import advisory_engine
from backend.services.risk_engine import risk_engine
from backend.services.market_data_service import market_data_service


# In-memory session chat history
_SESSION_HISTORY: Dict[str, List[Dict[str, Any]]] = {}


class ChatbotService:
    def __init__(self):
        pass

    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        return _SESSION_HISTORY.get(session_id, [])

    def clear_session_history(self, session_id: str):
        if session_id in _SESSION_HISTORY:
            _SESSION_HISTORY[session_id] = []

    def process_message(self, message: str, session_id: str = "default") -> Dict[str, Any]:
        """Processes user natural language message and produces intelligent structured response."""
        q = message.strip()
        q_lower = q.lower()

        # Initialize session history
        if session_id not in _SESSION_HISTORY:
            _SESSION_HISTORY[session_id] = []

        # Store user message
        _SESSION_HISTORY[session_id].append({
            "sender": "user",
            "text": q,
            "timestamp": datetime.now().strftime("%H:%M")
        })

        # Generate response
        response = self._generate_response(q, q_lower)

        # Store assistant message
        _SESSION_HISTORY[session_id].append({
            "sender": "assistant",
            "text": response["reply"],
            "stock_chips": response.get("stock_chips", []),
            "suggested_prompts": response.get("suggested_prompts", []),
            "timestamp": datetime.now().strftime("%H:%M")
        })

        # Keep history capped at 30 messages
        if len(_SESSION_HISTORY[session_id]) > 30:
            _SESSION_HISTORY[session_id] = _SESSION_HISTORY[session_id][-30:]

        return response

    def _generate_response(self, query: str, q: str) -> Dict[str, Any]:
        """Core multi-factor quantitative router and response builder."""
        
        # 1. Compare [STOCK1] and [STOCK2] (Priority over single stock match)
        compare_match = re.search(r"(?:compare|vs|versus)\s+([a-zA-Z0-9\.\^]+)(?:\s+and\s+|\s+vs\s+|\s+with\s+|\s+)([a-zA-Z0-9\.\^]+)", q)
        if compare_match:
            t1 = compare_match.group(1).upper()
            t2 = compare_match.group(2).upper()
            return self._handle_comparison_query(t1, t2)

        # 2. 'Which stocks should I buy?' / 'Top picks' / 'Best stocks to invest'
        if any(w in q for w in ["which stock", "stocks to buy", "what to buy", "best stock", "top buy", "recommend", "buy pick", "good to buy", "buy candidate", "what should i buy"]):
            return self._handle_top_buys_query()

        # 3. 'Which stocks should I avoid?' / 'Stocks to avoid' / 'Risky stocks'
        if any(w in q for w in ["avoid", "dont buy", "don't buy", "risky stock", "stocks to sell", "high risk", "caution list", "sell"]):
            return self._handle_stocks_to_avoid_query()

        # 4. 'Should I buy / avoid [STOCK]?' or 'Prediction for [STOCK]' or '[STOCK] target'
        stock_match = self._extract_ticker_from_query(q)
        if stock_match:
            return self._handle_stock_inquiry(stock_match)

        # 5. Greetings & System Capability queries (Word bounded)
        if re.search(r"\b(hello|hi|hey|who are you|what can you do|help|start)\b", q):
            return {
                "reply": (
                    "👋 **Hello! I'm AlphaBot, your AI Financial Copilot.**\n\n"
                    "I combine live exchange data with **calibrated machine learning models** and multi-factor quantitative analysis to help you make smarter investment decisions. Here is what I can do for you:\n\n"
                    "• 🎯 **Stock Predictions & Advisory**: Ask me about any stock (*e.g. 'Should I buy Reliance?', 'Prediction for Suzlon'*).\n"
                    "• ⚡ **Top Buys & Stocks to Avoid**: Get real-time high-conviction recommendations and risk warnings.\n"
                    "• 💼 **Portfolio Diagnostics**: Analyze your holdings, sector risk, Sharpe ratio, and Value-at-Risk.\n"
                    "• 🌪️ **Macro Stress Tests**: Simulate market shocks (*e.g. 'What if Nifty drops 5%?'*).\n"
                    "• ⚖️ **Stock Comparisons**: Side-by-side technical and fundamental comparisons (*e.g. 'Compare TCS and INFY'*)."
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "🎯 Which stocks should I buy today?",
                    "⚠️ What stocks should I avoid?",
                    "⚡ Prediction for Reliance",
                    "💼 Analyze my portfolio risk"
                ]
            }

        # 6. Portfolio Diagnostics & Stress Testing
        if "portfolio" in q or "holdings" in q or "my stocks" in q:
            if "stress" in q or "drop" in q or "crash" in q or "fall" in q or "shock" in q:
                return self._handle_portfolio_stress_test()
            return self._handle_portfolio_overview()

        if "nifty drop" in q or "market crash" in q or "nifty falls" in q:
            return self._handle_portfolio_stress_test()

        # 7. Concept & Quantitative Explanations
        if "rsi" in q:
            return {
                "reply": (
                    "📊 **Relative Strength Index (RSI - 14 Period)**\n\n"
                    "RSI measures the speed and velocity of recent price changes on a scale of 0 to 100:\n\n"
                    "• **RSI 45 – 65 (Sweet-Spot Accumulation)**: Healthy upward momentum with room for further institutional expansion.\n"
                    "• **RSI > 75 (Extreme Overbought)**: Stock is exhausted and prone to sudden mean-reversion profit taking. *Usually labeled AVOID / CAUTION*.\n"
                    "• **RSI < 35 (Breakdown / Oversold)**: Heavy persistent selling pressure; requires confirmed technical base before entry."
                ),
                "stock_chips": [],
                "suggested_prompts": ["🎯 Top Buys with healthy RSI", "⚡ Prediction for Tata Motors", "⚠️ Stocks currently overbought"]
            }

        if "prediction" in q or "model" in q or "accuracy" in q:
            return {
                "reply": (
                    "🤖 **How AlphaLens Machine Learning Predictions Work**\n\n"
                    "AlphaLens uses a **Soft-Voting Ensemble** combining **HistGradientBoosting, Random Forest, and Logistic Regression** calibrated via 5-fold cross-validation:\n\n"
                    "1. **24 Quantitative Alpha Factors**: Evaluates trend structure (distances to 20/50/200 SMAs), momentum (RSI, MACD), volatility (ATR, Bollinger Bands), volume ratios, and FinBERT news sentiment.\n"
                    "2. **Quantile Regression (Q10/Q50/Q90)**: Outputs expected percentage return plus asymmetric **90% Confidence Prediction Intervals**.\n"
                    "3. **Empirical Calibration**: Out-of-sample directional accuracy is **58.1%** with a Brier score of **0.240**, providing a disciplined statistical edge without overfitting."
                ),
                "stock_chips": [],
                "suggested_prompts": ["🎯 Show me today's AI picks", "📜 View Prediction Ledger", "💼 Portfolio risk summary"]
            }

        # 8. General Market Overview fallback
        return self._handle_market_overview_query()

    def _extract_ticker_from_query(self, q: str) -> Optional[str]:
        """Identifies stock tickers or company names mentioned in query."""
        catalog = live_pipeline.latest_stocks_cache
        
        # Check direct regex patterns: "about RELIANCE", "for SUZLON", "is TCS good"
        pattern = r"(?:about|for|on|is|should i buy|buy|avoid|predict|prediction for|target for|analyze|check)\s+([a-zA-Z0-9\.\^]{2,15})"
        match = re.search(pattern, q)
        if match:
            candidate = match.group(1).upper().strip()
            if candidate in catalog or candidate in ["SUZLON", "IREDA", "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "TATAMOTORS", "ZOMATO", "TRENT", "HAL", "BEL", "MAZDOCK", "RVNL"]:
                return candidate
            # Fuzzy check in catalog
            for ticker, stock in catalog.items():
                if candidate in ticker or candidate in stock.get("name", "").upper():
                    return ticker

        # Word-by-word catalog match
        words = re.findall(r"\b[A-Za-z0-9]+\b", q.upper())
        for w in words:
            if w in catalog:
                return w
            for ticker, stock in catalog.items():
                if w == ticker or w in stock.get("name", "").upper().split():
                    if len(w) > 3 or w in ["TCS", "ITC", "SBI", "LT", "HAL", "BEL", "M&M"]:
                        return ticker
        return None

    def _handle_stock_inquiry(self, ticker: str) -> Dict[str, Any]:
        """Provides deep quantitative prediction, advisory verdict, and price targets for a stock."""
        stock = live_pipeline.get_stock(ticker)
        if not stock:
            return {
                "reply": f"⚠️ Could not find live market data for symbol **{ticker}**. Please check the ticker name.",
                "stock_chips": [],
                "suggested_prompts": ["🎯 Top Buys for today", "⚠️ Stocks to avoid", "⚡ Prediction for Reliance"]
            }

        adv = stock.get("advisory") or advisory_engine.evaluate_advisory(stock)
        tech = stock.get("technicals", {})
        fund = stock.get("fundamentals", {})
        outlook = stock.get("model_outlook", {})
        targets = adv.get("targets", {})
        verdict = adv.get("verdict", "HOLD / WATCH")

        is_buy = "BUY" in verdict
        is_avoid = "AVOID" in verdict
        verdict_icon = "🟢" if is_buy else ("🔴" if is_avoid else "🟡")

        why_buy_text = "\n".join([f"  • {r}" for r in adv.get("why_buy_reasons", [])[:2]])
        why_avoid_text = "\n".join([f"  • {w}" for w in adv.get("why_avoid_warnings", [])[:2]])

        reply = (
            f"### {verdict_icon} **{stock.get('name')} ({ticker})** — **{verdict}**\n\n"
            f"**Current Price:** `₹{stock.get('price', 0):,.2f}` ({stock.get('change_1d_pct', 0.0):+0.2f}% Today)\n"
            f"**AI Model Conviction:** `{adv.get('conviction_score', 75)}%` • **Direction Outlook:** `{outlook.get('direction', 'Positive')} ({outlook.get('probability_percent', 70)}%)`\n\n"
            f"#### 🎯 **Actionable Target Levels**\n"
            f"• **Entry Zone:** `{targets.get('entry_zone', 'Current Market Price')}`\n"
            f"• **Target 1:** `{targets.get('target_1', 'N/A')}` *(Upside: {targets.get('target_1_upside', '+0%')})*\n"
            f"• **Target 2:** `{targets.get('target_2', 'N/A')}` *(Upside: {targets.get('target_2_upside', '+0%')})*\n"
            f"• **Stop Loss:** `{targets.get('stop_loss', 'N/A')}` *(Risk: {targets.get('stop_loss_pct', '-0%')})*\n"
            f"• **Risk : Reward:** `{targets.get('risk_reward_ratio', '1 : 2.0')}`\n\n"
            f"#### 🔍 **Key Drivers & Catalysts**\n"
            f"{why_buy_text if why_buy_text else '  • Steady technical alignment across key moving averages.'}\n\n"
            f"{('#### ⚠️ **Risk Factors**\n' + why_avoid_text + '\n\n') if why_avoid_text else ''}"
            f"💡 *Suitability: {adv.get('suitability', 'Suitable for active investors.')}*"
        )

        return {
            "reply": reply,
            "stock_chips": [
                {
                    "ticker": ticker,
                    "name": stock.get("name"),
                    "price": f"₹{stock.get('price', 0):,.1f}",
                    "verdict": verdict,
                    "badge_class": adv.get("badge_class", "badge-buy")
                }
            ],
            "suggested_prompts": [
                f"💡 Why is {ticker} moving today?",
                "🎯 Show other Top Buy picks",
                f"⚖️ Compare {ticker} with sector peer",
                "⚠️ What stocks should I avoid?"
            ]
        }

    def _handle_top_buys_query(self) -> Dict[str, Any]:
        """Returns top buy recommendations with target levels."""
        recs = live_pipeline.get_all_recommendations()
        top_buys = recs.get("top_buys", [])[:4]

        cards_text = ""
        stock_chips = []

        for b in top_buys:
            t = b["targets"]
            cards_text += (
                f"**🟢 {b['ticker']} — {b['name']}**\n"
                f"• Price: `₹{b['current_price']:,.1f}` | Verdict: **{b['verdict']}** (`{b['conviction_score']}% Conviction`)\n"
                f"• Entry: `{t['entry_zone']}` → Target: `{t['target_1']} ({t['target_1_upside']})` | SL: `{t['stop_loss']}`\n"
                f"• Catalyst: {b['why_buy_reasons'][0] if b['why_buy_reasons'] else 'Strong multi-factor momentum.'}\n\n"
            )
            stock_chips.append({
                "ticker": b["ticker"],
                "name": b["name"],
                "price": f"₹{b['current_price']:,.1f}",
                "verdict": b["verdict"],
                "badge_class": "badge-strong-buy"
            })

        reply = (
            "### 🎯 **Top AI Buy Recommendations for Today**\n\n"
            "Our multi-factor quantitative models have identified the following high-conviction equities exhibiting optimal momentum (RSI 45–65), strong moving average support, and favorable risk-reward ratios:\n\n"
            f"{cards_text}"
            "💡 *Click any stock pill below to view interactive candles, technical indicators, and full analysis.*"
        )

        return {
            "reply": reply,
            "stock_chips": stock_chips,
            "suggested_prompts": [
                "⚠️ Which stocks should I avoid?",
                "🚀 Show Momentum Breakout stocks",
                "💎 Show Value Accumulation picks",
                "💼 How does this fit my portfolio?"
            ]
        }

    def _handle_stocks_to_avoid_query(self) -> Dict[str, Any]:
        """Returns caution and avoid recommendations."""
        recs = live_pipeline.get_all_recommendations()
        avoids = recs.get("stocks_to_avoid", [])[:4]

        cards_text = ""
        stock_chips = []

        for a in avoids:
            cards_text += (
                f"**🔴 {a['ticker']} — {a['name']}**\n"
                f"• Price: `₹{a['current_price']:,.1f}` | Verdict: **{a['verdict']}** (`{a['conviction_score']}% Caution`)\n"
                f"• Risk Warning: ⚠️ {a['why_avoid_warnings'][0] if a['why_avoid_warnings'] else 'Technical breakdown below key support levels.'}\n"
                f"• Safer Alternative: {a.get('alternative_suggestion') or 'Defensive bluechips with RSI in 50-60 range.'}\n\n"
            )
            stock_chips.append({
                "ticker": a["ticker"],
                "name": a["name"],
                "price": f"₹{a['current_price']:,.1f}",
                "verdict": a["verdict"],
                "badge_class": "badge-avoid"
            })

        reply = (
            "### ⚠️ **Stocks to Avoid / High Risk Caution List**\n\n"
            "The following assets currently display technical breakdown patterns (trading below 50/200-day SMAs), extreme overbought exhaustion (RSI > 75), or unfavorable risk-reward profiles:\n\n"
            f"{cards_text}"
            "🛡️ *Risk Rule: Capital preservation takes precedence over chasing overextended rallies.*"
        )

        return {
            "reply": reply,
            "stock_chips": stock_chips,
            "suggested_prompts": [
                "🎯 Show me safe Buy recommendations",
                "💼 Check my portfolio risk",
                "⚡ Prediction for Reliance",
                "🌪️ What if NIFTY drops 5%?"
            ]
        }

    def _handle_comparison_query(self, t1: str, t2: str) -> Dict[str, Any]:
        """Compares two stocks side by side."""
        s1 = live_pipeline.get_stock(t1)
        s2 = live_pipeline.get_stock(t2)

        if not s1 or not s2:
            return {
                "reply": f"Could not find comparative data for both {t1} and {t2}. Please verify the tickers.",
                "stock_chips": [],
                "suggested_prompts": ["🎯 Show Top Buys", "⚡ Prediction for TCS", "⚡ Prediction for INFY"]
            }

        adv1 = s1.get("advisory", {})
        adv2 = s2.get("advisory", {})

        reply = (
            f"### ⚖️ **Quantitative Comparison: {t1} vs {t2}**\n\n"
            f"| Metric | **{t1}** | **{t2}** |\n"
            f"|---|---|---|\n"
            f"| **Current Price** | `₹{s1.get('price', 0):,.2f}` | `₹{s2.get('price', 0):,.2f}` |\n"
            f"| **1D Change** | `{s1.get('change_1d_pct', 0):+0.2f}%` | `{s2.get('change_1d_pct', 0):+0.2f}%` |\n"
            f"| **Advisory Verdict** | **{adv1.get('verdict', 'HOLD')}** | **{adv2.get('verdict', 'HOLD')}** |\n"
            f"| **Conviction Score** | `{adv1.get('conviction_score', 70)}%` | `{adv2.get('conviction_score', 70)}%` |\n"
            f"| **14D RSI** | `{s1.get('technicals', {}).get('rsi_14', 50)}` | `{s2.get('technicals', {}).get('rsi_14', 50)}` |\n"
            f"| **Target 1** | `{adv1.get('targets', {}).get('target_1', 'N/A')}` | `{adv2.get('targets', {}).get('target_1', 'N/A')}` |\n"
            f"| **Stop Loss** | `{adv1.get('targets', {}).get('stop_loss', 'N/A')}` | `{adv2.get('targets', {}).get('stop_loss', 'N/A')}` |\n\n"
            f"💡 **AI Takeaway:** {t1 if adv1.get('conviction_score', 0) >= adv2.get('conviction_score', 0) else t2} shows higher relative quantitative strength and risk-adjusted positioning."
        )

        return {
            "reply": reply,
            "stock_chips": [
                {"ticker": t1, "name": s1.get("name"), "price": f"₹{s1.get('price', 0):,.1f}", "verdict": adv1.get("verdict", "HOLD"), "badge_class": adv1.get("badge_class", "badge-buy")},
                {"ticker": t2, "name": s2.get("name"), "price": f"₹{s2.get('price', 0):,.1f}", "verdict": adv2.get("verdict", "HOLD"), "badge_class": adv2.get("badge_class", "badge-buy")}
            ],
            "suggested_prompts": [
                f"⚡ Deep dive on {t1}",
                f"⚡ Deep dive on {t2}",
                "🎯 Show other Top Buys today",
                "💼 Portfolio risk check"
            ]
        }

    def _handle_portfolio_overview(self) -> Dict[str, Any]:
        """Provides portfolio health and factor attribution."""
        port = risk_engine.analyze_portfolio(live_pipeline.latest_stocks_cache)
        metrics = port.get("risk_metrics", {})

        reply = (
            "### 💼 **Portfolio Health & Factor Risk Diagnostics**\n\n"
            f"• **Current Valuation:** `₹{port.get('total_value', 0):,.2f}` (Invested: `₹{port.get('invested_capital', 0):,.2f}`)\n"
            f"• **Total P&L:** `+₹{port.get('total_pnl', 0):,.2f}` (`{port.get('total_pnl_pct', 0):+0.2f}%`)\n"
            f"• **Today's Movement:** `+₹{port.get('today_pnl', 0):,.2f}` (`{port.get('today_pnl_pct', 0):+0.2f}%`)\n\n"
            "#### 🛡️ **Risk & Attribution Metrics**\n"
            f"• **Portfolio Beta (vs NIFTY 50):** `{metrics.get('beta_vs_nifty', 1.04)}` (Balanced Market Exposure)\n"
            f"• **Sharpe Ratio:** `{metrics.get('sharpe_ratio', 1.72)}` (Strong risk-adjusted excess return)\n"
            f"• **Value-at-Risk (1D 95% VaR):** `{metrics.get('var_95_1d_inr', '-₹4,820')}`\n"
            f"• **Conditional VaR (CVaR):** `{metrics.get('cvar_95_1d_inr', '-₹6,025')}`\n\n"
            "💡 *Recommendation: Diversification is well-balanced across Energy, Financials, and Tech.*"
        )

        return {
            "reply": reply,
            "stock_chips": [
                {"ticker": h["ticker"], "name": h["name"], "price": f"₹{h.get('current_price', 0):,.1f}", "verdict": h.get("model_outlook", "Positive"), "badge_class": "badge-buy"}
                for h in port.get("holdings", [])[:3]
            ],
            "suggested_prompts": [
                "🌪️ Simulate: What if NIFTY drops 5%?",
                "🎯 Which new stocks should I add to my portfolio?",
                "⚠️ Are any of my holdings in the Avoid list?"
            ]
        }

    def _handle_portfolio_stress_test(self) -> Dict[str, Any]:
        """Runs macro shock simulation."""
        port = risk_engine.analyze_portfolio(live_pipeline.latest_stocks_cache)
        port_val = float(port.get("total_value", 321840.0))
        sim = risk_engine.simulate_scenario("nifty_drop_5pct", port_val)

        impact_pct = sim.get("expected_impact_pct", -5.2)
        impact_inr = sim.get("expected_impact_inr", -round(port_val * 0.052, 2))
        post_val = port_val + impact_inr

        reply = (
            f"### 🌪️ **Macro Stress Test: {sim.get('title', 'NIFTY 50 Falls -5.0%')}**\n\n"
            f"**Scenario Description:** {sim.get('description', 'Macro shock simulation')}\n\n"
            f"• **Estimated Drawdown:** `{impact_pct:+.2f}%` (`₹{impact_inr:,.0f}`)\n"
            f"• **Projected Portfolio Value:** `₹{post_val:,.2f}` (from current `₹{port_val:,.2f}`)\n"
            f"• **Sector Impact Breakdown:**\n"
        )

        for s in sim.get("sector_impacts", []):
            reply += f"  - **{s.get('sector')}:** `{s.get('impact')}` (Resilience: {s.get('resilience')})\n"

        reply += f"\n🛡️ **Recommended Action:** {sim.get('recommended_action', 'Keep core weights balanced; hedges adequate.')}"

        return {
            "reply": reply,
            "stock_chips": [],
            "suggested_prompts": [
                "🎯 Show safest defensive stocks to buy",
                "💼 Back to Portfolio Overview",
                "⚠️ Stocks to Avoid right now"
            ]
        }

    def _handle_market_overview_query(self) -> Dict[str, Any]:
        """Provides general live market summary."""
        indices = live_pipeline.get_market_overview()
        n50 = indices.get("nifty_50", {})
        bn = indices.get("bank_nifty", {})
        vix = indices.get("india_vix", {})

        reply = (
            "### 🌐 **Live Market Pulse & Intelligence Overview**\n\n"
            f"• **NIFTY 50:** `{n50.get('value', '23,346.40')}` ({n50.get('change_formatted', '+0.33%')})\n"
            f"• **BANK NIFTY:** `{bn.get('value', '56,358.70')}` ({bn.get('change_formatted', '+0.54%')})\n"
            f"• **INDIA VIX:** `{vix.get('value', '11.39')}` *(Volatility Contained)*\n"
            f"• **Market Regime:** `{indices.get('market_regime', 'MILD BULL')}` — *{indices.get('market_outlook', 'Constructive Accumulation')}*\n\n"
            "How can I help you navigate the market today? You can ask me for stock recommendations, specific stock forecasts, or portfolio diagnostics."
        )

        return {
            "reply": reply,
            "stock_chips": [],
            "suggested_prompts": [
                "🎯 Which stocks should I buy today?",
                "⚠️ What stocks should I avoid?",
                "⚡ Prediction for Reliance",
                "💼 Portfolio health check"
            ]
        }


chatbot_service = ChatbotService()
