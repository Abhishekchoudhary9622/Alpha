"""
AlphaLens AI Financial Copilot Chatbot Engine (Powered by Google Gemini & Quantitative ML)
Context-aware quantitative reasoning agent that answers user queries about:
- Stock predictions, live market data, and top buy/avoid advisories
- IPOs (Which to apply vs avoid, Grey Market Premiums / GMP, listing gains)
- Mutual Funds (Category rankings, 3Y/5Y returns, personalized risk suitability)
- Futures & Options / F&O (Option chains, PCR, Max Pain, trading strategies)
- General financial education, Indian taxation (LTCG/STCG), compounding, SIP
- Platform onboarding, broker integration (Zerodha/Upstox), CAS statement parser, and AA consent.
"""

import os
import re
import json
import time
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from backend.pipeline.live_pipeline import live_pipeline
from backend.services.advisory_engine import advisory_engine
from backend.services.risk_engine import risk_engine
from backend.services.market_data_service import market_data_service
from backend.services.ipo_service import ipo_service
from backend.services.mutual_fund_service import mutual_fund_service
from backend.services.fno_service import fno_service


# In-memory session chat history
_SESSION_HISTORY: Dict[str, List[Dict[str, Any]]] = {}

# Google Gemini API Configuration (loaded securely from .env via os.getenv)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEFAULT_GEMINI_MODELS = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.7-flash", "gemini-2.5-flash-lite", "gemini-flash-latest"]


class ChatbotService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)

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

        # 1. First attempt generation via Google Gemini with Live Quant Context
        gemini_response = self._try_gemini_generation(q, session_id)
        if gemini_response and gemini_response.get("reply"):
            response = gemini_response
        else:
            # 2. Fall back to local high-precision quantitative & educational knowledge base
            response = self._generate_local_response(q, q_lower)

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

    # =========================================================================
    # Gemini AI Core Integration
    # =========================================================================
    def _try_gemini_generation(self, user_query: str, session_id: str) -> Optional[Dict[str, Any]]:
        """Invokes Google Gemini with injected live quantitative market & financial intelligence."""
        api_key = os.getenv("GEMINI_API_KEY", self.api_key)
        if not api_key:
            return None

        # Assemble live system context
        context_summary = self._build_live_context_summary()

        system_instruction = (
            "You are AlphaBot (also known as ChatBot / AI Financial Copilot), an institutional-grade AI financial analyst, "
            "quantitative strategist, and customer support advisor for AlphaLens (FinaX) specializing in the Indian (NSE/BSE) "
            "and global financial markets.\n\n"
            "Your capabilities include:\n"
            "1. IPOs: Recommend which IPOs to APPLY for (listing gains vs long term) vs AVOID based on Grey Market Premium (GMP), "
            "valuations (P/E), issue size, and promoter pedigree.\n"
            "2. Mutual Funds: Recommend top direct mutual funds (Flexi Cap, Large Cap Index, Mid Cap, Small Cap, ELSS) with CAGR, "
            "expense ratios, and personalized risk profiles (Conservative, Moderate, Aggressive).\n"
            "3. Futures & Options (F&O): Explain option chain metrics, PCR, Max Pain, and suggest risk-defined strategies (Bull Call Spread, Iron Condor).\n"
            "4. Stocks & Equities: Explain stock forecasts, technicals (RSI, 20/50/200 EMAs), fundamentals (P/E, ROE, D/E), and AlphaLens multi-factor predictions.\n"
            "5. General Financial Education & Taxes: Explain SIP, compounding, Indian equity taxation (LTCG 12.5%, STCG 20%), stop loss, and position sizing.\n"
            "6. Platform Support: Help users connect brokers (Zerodha Kite, Upstox), upload CAS statements (CAMS/KFintech), and use Account Aggregator (AA).\n\n"
            "Style Guide:\n"
            "- Format with clean Markdown headers (###), bold key terms, tables where helpful, and emoji badges (🟢, 🔴, 🟡, 🎯, 📊, ⚡).\n"
            "- Always be professional, disciplined, and educational. Add clear actionable takeaways and risk management rules.\n\n"
            f"=== LIVE MARKET & QUANTITATIVE DATA CONTEXT ===\n{context_summary}\n===============================================\n"
        )

        # Build conversation turns from session history
        history_msgs = []
        recent_history = _SESSION_HISTORY.get(session_id, [])[-6:]
        for h in recent_history:
            role = "user" if h.get("sender") == "user" else "model"
            history_msgs.append({"role": role, "parts": [{"text": h.get("text", "")}]})

        if not history_msgs or history_msgs[-1]["parts"][0]["text"] != user_query:
            history_msgs.append({"role": "user", "parts": [{"text": user_query}]})

        payload = {
            "system_instruction": {"parts": [{"text": system_instruction}]},
            "contents": history_msgs,
            "generationConfig": {
                "temperature": 0.4,
                "topP": 0.9,
                "maxOutputTokens": 1024
            }
        }

        # Try active models
        for model in DEFAULT_GEMINI_MODELS:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            try:
                resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=8)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            raw_text = parts[0]["text"]
                            chips, prompts = self._generate_contextual_chips_and_prompts(user_query, raw_text)
                            return {
                                "reply": raw_text,
                                "stock_chips": chips,
                                "suggested_prompts": prompts
                            }
            except Exception:
                continue

        return None

    def _build_live_context_summary(self) -> str:
        """Constructs rich string representation of live platform data for Gemini."""
        overview = live_pipeline.get_market_overview()
        n50 = overview.get("nifty_50", {})
        bn = overview.get("bank_nifty", {})
        vix = overview.get("india_vix", {})
        regime = overview.get("market_regime", "MILD BULL")

        recs = live_pipeline.get_all_recommendations()
        buys = recs.get("top_buys", [])[:3]
        avoids = recs.get("stocks_to_avoid", [])[:3]

        ipos = ipo_service.get_active_and_upcoming_ipos()[:4]
        funds = mutual_fund_service.get_all_funds()[:4]
        fno = fno_service.get_index_option_chain_summary("NIFTY")

        lines = [
            f"1. Market Indices: NIFTY 50 = {n50.get('value', '24850')} ({n50.get('change_formatted', '+0.3%')}), BANK NIFTY = {bn.get('value', '52340')}, INDIA VIX = {vix.get('value', '11.4')}, Regime = {regime}.",
            "2. Top Stock Buy Recommendations:",
        ]
        for b in buys:
            lines.append(f"   - {b['ticker']} ({b['name']}): Price ₹{b['current_price']}, Verdict {b['verdict']}, Conviction {b['conviction_score']}%, Target {b['targets']['target_1']}")

        lines.append("3. Stocks to Avoid / Caution List:")
        for a in avoids:
            lines.append(f"   - {a['ticker']} ({a['name']}): Price ₹{a['current_price']}, Verdict {a['verdict']}, Risk {a['why_avoid_warnings'][0] if a['why_avoid_warnings'] else 'Breakdown'}")

        lines.append("4. Live / Upcoming IPOs:")
        for ipo in ipos:
            lines.append(f"   - {ipo['name']} ({ipo['symbol']}): Price Band {ipo['price_band']}, GMP ₹{ipo['gmp_inr']} ({ipo['gmp_percent']}%), Verdict: {ipo['verdict']}")

        lines.append("5. Top Mutual Funds:")
        for f in funds:
            lines.append(f"   - {f['name']} ({f['category']}): 3Y CAGR {f['cagr_3y']}%, 5Y CAGR {f['cagr_5y']}%, Expense {f['expense_ratio']}%, Verdict: {f['verdict']}")

        lines.append(f"6. F&O Derivatives (NIFTY): Spot {fno['spot_price']}, PCR OI {fno['put_call_ratio_oi']}, Max Pain Strike {fno['max_pain_strike']}, Support {fno['major_support_strike']}, Resistance {fno['major_resistance_strike']}, Strategy: {fno['recommended_strategy']['name']}")

        return "\n".join(lines)

    def _generate_contextual_chips_and_prompts(self, query: str, reply_text: str) -> tuple:
        """Extracts relevant chips and prompts based on user query."""
        q = query.lower()
        chips = []
        prompts = []

        # Stock chips
        if "ipo" in q:
            prompts = ["🚀 Which IPO should I apply for?", "📊 Current IPO GMP & Subscriptions", "💎 Top Mutual Funds to invest", "🎯 Top Stock Buys today"]
        elif "mutual fund" in q or "sip" in q or "fund" in q:
            prompts = ["💎 Which Mutual Fund is best for me?", "📈 What is SIP and compounding?", "🧾 Tax on Mutual Funds (LTCG)", "🎯 Top Stock Buys today"]
        elif "f&o" in q or "option" in q or "futures" in q or "pcr" in q or "call" in q or "put" in q:
            prompts = ["⚡ NIFTY Option Chain & PCR", "🎯 Options Strategy for today", "🌪️ What is India VIX?", "🛡️ Stop Loss & Position Sizing"]
        elif "avoid" in q or "risk" in q:
            prompts = ["🎯 Show me safe Top Buys", "💼 Check my portfolio risk", "🌪️ What if NIFTY drops 5%?", "⚡ Prediction for Reliance"]
        else:
            prompts = ["🎯 Which stocks should I buy today?", "🚀 Which IPO should I apply for?", "💎 Which Mutual Fund is best?", "⚡ NIFTY Option Chain & F&O"]

        # If a stock is mentioned, attach chip
        for ticker in ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "TATAMOTORS", "ZOMATO", "SUZLON"]:
            if ticker in query.upper() or ticker in reply_text.upper():
                stock = live_pipeline.get_stock(ticker)
                if stock:
                    chips.append({
                        "ticker": ticker,
                        "name": stock.get("name"),
                        "price": f"₹{stock.get('price', 0):,.1f}",
                        "verdict": stock.get("advisory", {}).get("verdict", "BUY"),
                        "badge_class": stock.get("advisory", {}).get("badge_class", "badge-buy")
                    })
                if len(chips) >= 2:
                    break

        return chips, prompts

    # =========================================================================
    # Local Quantitative & Educational Router (Fallback & Offline)
    # =========================================================================
    def _generate_local_response(self, query: str, q: str) -> Dict[str, Any]:
        """Core multi-factor quantitative router when Gemini API is offline."""
        
        # 1. Compare [STOCK1] and [STOCK2]
        compare_match = re.search(r"(?:compare|vs|versus)\s+([a-zA-Z0-9\.\^]+)(?:\s+and\s+|\s+vs\s+|\s+with\s+|\s+)([a-zA-Z0-9\.\^]+)", q)
        if compare_match:
            t1 = compare_match.group(1).upper()
            t2 = compare_match.group(2).upper()
            return self._handle_comparison_query(t1, t2)

        # 2. IPO Queries
        if any(w in q for w in ["ipo", "ipos", "gmp", "grey market", "listing gain", "which ipo", "apply for ipo", "ipo apply"]):
            return self._handle_ipo_query(q)

        # 3. Mutual Fund Queries
        if any(w in q for w in ["mutual fund", "mutual funds", "mf", "which mutual fund", "best mutual fund", "flexi cap", "small cap fund", "index fund", "elss"]):
            return self._handle_mutual_fund_query(q)

        # 4. F&O / Options Queries
        if any(w in q for w in ["f&o", "fno", "option chain", "pcr", "max pain", "call option", "put option", "futures", "options strategy", "open interest"]):
            return self._handle_fno_query(q)

        # 5. Top buys
        if any(w in q for w in ["which stock", "stocks to buy", "what to buy", "best stock", "top buy", "recommend", "buy pick", "good to buy", "buy candidate", "what should i buy"]):
            return self._handle_top_buys_query()

        # 6. Stocks to avoid
        if any(w in q for w in ["which stocks to avoid", "stocks to avoid", "what to avoid", "dont buy", "don't buy", "risky stock", "stocks to sell", "high risk", "caution list", "avoid stocks"]):
            return self._handle_stocks_to_avoid_query()

        # 7. Platform support
        platform_res = self._handle_platform_support_query(q)
        if platform_res:
            return platform_res

        # 8. Financial education
        edu_res = self._handle_financial_education_query(q)
        if edu_res:
            return edu_res

        # 9. Portfolio
        if "portfolio" in q or "holdings" in q or "my stocks" in q:
            if "stress" in q or "drop" in q or "crash" in q or "fall" in q or "shock" in q:
                return self._handle_portfolio_stress_test()
            return self._handle_portfolio_overview()

        # 10. Specific stock inquiry
        stock_match = self._extract_ticker_from_query(q)
        if stock_match:
            return self._handle_stock_inquiry(stock_match)

        # 11. Greetings
        if re.search(r"^(hello|hi|hey|who are you|what can you do|help|namaste|good morning|good evening)\b", q):
            return {
                "reply": (
                    "👋 **Hello! I'm AlphaBot, your AI Financial & Market Intelligence Copilot.**\n\n"
                    "Powered by Google Gemini and real-time quantitative models, here is how I can assist you:\n\n"
                    "• 🚀 **IPO Intelligence**: Get clear **APPLY vs AVOID** verdicts, Grey Market Premiums (GMP), and listing gain projections.\n"
                    "• 💎 **Mutual Funds Advisory**: Discover top-ranked Flexi Cap, Index, and Small Cap funds tailored to your risk profile.\n"
                    "• ⚡ **F&O & Derivatives**: Analyze Option Chains, PCR, Max Pain strikes, and options strategies.\n"
                    "• 🎯 **Stock Predictions**: 7-day multi-factor forecasts, price targets, entry zones, and stop losses.\n"
                    "• 📚 **Financial Education**: Explaining SIP, Indian equity taxation (LTCG/STCG), P/E ratio, RSI, and risk management.\n"
                    "• 🔗 **Broker & CAS Integration**: Step-by-step help linking Zerodha Kite, Upstox, or uploading CAMS/KFintech CAS PDFs."
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "🚀 Which IPO should I apply for today?",
                    "💎 Which Mutual Fund is best for me?",
                    "⚡ NIFTY Option Chain & PCR",
                    "🎯 Which stocks should I buy today?",
                    "⚠️ What stocks should I avoid?"
                ]
            }

        # 12. General fallback
        return self._handle_general_reasoning_query(query, q)

    # =========================================================================
    # Specialized Domain Handlers (IPOs, Mutual Funds, F&O)
    # =========================================================================
    def _handle_ipo_query(self, q: str) -> Dict[str, Any]:
        """Provides expert IPO recommendations, GMP analysis, and apply/avoid verdicts."""
        ipos = ipo_service.get_all_ipos()
        
        # Check if asking about specific IPO
        for ipo in ipos:
            if ipo["symbol"].lower() in q or ipo["id"] in q or ipo["name"].lower().split()[0] in q:
                v_icon = "🟢" if "APPLY" in ipo["verdict"] and "AVOID" not in ipo["verdict"] else ("🔴" if "AVOID" in ipo["verdict"] else "🟡")
                pros_text = "\n".join([f"  • {p}" for p in ipo.get("pros", [])])
                cons_text = "\n".join([f"  • {c}" for c in ipo.get("cons", [])])

                reply = (
                    f"### {v_icon} **IPO Deep Dive: {ipo['name']} ({ipo['symbol']})**\n\n"
                    f"**Verdict:** `{ipo['verdict']}` • **AI Conviction:** `{ipo['conviction_score']}%`\n"
                    f"• **Price Band:** `{ipo['price_band']}` | **Lot Size:** `{ipo['lot_size']} shares` (Min Inv: `₹{ipo['min_investment']:,}`)\n"
                    f"• **Issue Size:** `₹{ipo['issue_size_cr']:,} Cr` | **Status:** `{ipo['status']}`\n"
                    f"• **Current GMP:** `+₹{ipo['gmp_inr']}` (**+{ipo['gmp_percent']}% Expected Listing Pop**)\n"
                    f"• **Valuation P/E:** `{ipo['pe_ratio']}x` (Sector Avg: `{ipo['sector_pe']}x`)\n\n"
                    f"#### 🔍 **Key Strengths (Why Apply):**\n{pros_text}\n\n"
                    f"#### ⚠️ **Key Risks & Concerns:**\n{cons_text}\n\n"
                    f"💡 **Final Takeaway:** {ipo['recommendation_summary']}"
                )
                return {
                    "reply": reply,
                    "stock_chips": [],
                    "suggested_prompts": [
                        "🚀 Which other IPOs should I apply for?",
                        "💎 Top Mutual Funds to invest in",
                        "🎯 Top Stock Buys for today",
                        "⚡ Prediction for Reliance"
                    ]
                }

        # General IPO summary
        applies = [ipo for ipo in ipos if "APPLY" in ipo["verdict"] and "AVOID" not in ipo["verdict"]][:2]
        avoids = [ipo for ipo in ipos if "AVOID" in ipo["verdict"] or "CAUTION" in ipo["verdict"]][:2]

        applies_text = ""
        for a in applies:
            applies_text += (
                f"• **🟢 {a['name']} ({a['symbol']}):** `{a['verdict']}`\n"
                f"  - Price: `{a['price_band']}` | GMP: `+₹{a['gmp_inr']} (+{a['gmp_percent']}%)`\n"
                f"  - Rationale: {a['pros'][0]}\n\n"
            )

        avoids_text = ""
        for av in avoids:
            avoids_text += (
                f"• **🔴 {av['name']} ({av['symbol']}):** `{av['verdict']}`\n"
                f"  - Price: `{av['price_band']}` | GMP: `+₹{av['gmp_inr']} (+{av['gmp_percent']}%)`\n"
                f"  - Caution: {av['cons'][0]}\n\n"
            )

        reply = (
            "### 🚀 **AlphaLens IPO Recommendation Radar (Active & Upcoming)**\n\n"
            "Our quantitative IPO framework evaluates Grey Market Premium (GMP), promoter pedigree, anchor book quality, and relative valuation:\n\n"
            f"#### 🟢 **Recommended to APPLY:**\n{applies_text}"
            f"#### ⚠️ **CAUTION / AVOID List:**\n{avoids_text}"
            "💡 *Pro-Tip: Always apply through your linked broker (Zerodha Kite / Upstox) via UPI ASBA before 4:30 PM on the closing day.*"
        )

        return {
            "reply": reply,
            "stock_chips": [],
            "suggested_prompts": [
                "🔍 Details on Bajaj Housing Finance IPO",
                "🔍 Details on NTPC Green Energy IPO",
                "💎 Which Mutual Fund is better for wealth creation?",
                "🎯 Top Stock Buys today"
            ]
        }

    def _handle_mutual_fund_query(self, q: str) -> Dict[str, Any]:
        """Provides expert mutual fund recommendations across risk categories."""
        if "flexi" in q:
            funds = mutual_fund_service.get_funds_by_category("Flexi Cap")
            cat_title = "Flexi Cap Funds (Core All-Weather Wealth Compounders)"
        elif "small" in q:
            funds = mutual_fund_service.get_funds_by_category("Small Cap")
            cat_title = "Small Cap Funds (High Growth & Aggressive Alpha)"
        elif "mid" in q:
            funds = mutual_fund_service.get_funds_by_category("Mid Cap")
            cat_title = "Mid Cap Funds (Rapid Earnings Growth Leaders)"
        elif "index" in q or "large" in q:
            funds = mutual_fund_service.get_funds_by_category("Index")
            cat_title = "Low-Cost Large Cap & Index Funds"
        elif "elss" in q or "tax" in q:
            funds = mutual_fund_service.get_funds_by_category("ELSS")
            cat_title = "ELSS Tax Saver Funds (Section 80C Deduction)"
        else:
            # Full personalized portfolio recommendation
            rec = mutual_fund_service.recommend_portfolio("moderate", 5)
            alloc_text = ""
            for a in rec["recommended_allocation"]:
                alloc_text += f"• **{a['fund']}** (`{a['category']}`) — **{a['weight_pct']}% Allocation**\n  *{a['rationale']}*\n\n"

            reply = (
                f"### 💎 **Recommended Mutual Fund Portfolio: {rec['strategy_name']}**\n\n"
                f"**Target Horizon:** `{rec['horizon_years']} Years` • **Expected Return:** `{rec['expected_cagr_range']}`\n\n"
                f"#### 📊 **Optimal Asset Allocation:**\n{alloc_text}"
                f"#### 💡 **Wealth-Building Pro-Tips:**\n"
                f"• Always invest in **Direct - Growth** plans to save 0.5%–1.0% annual distributor commissions.\n"
                f"• Set up automated monthly SIPs on your salary credit date for disciplined rupee-cost averaging.\n"
                f"• Apply an annual **10% Step-Up SIP** to double your final 15-year wealth corpus."
            )
            return {
                "reply": reply,
                "stock_chips": [],
                "suggested_prompts": [
                    "🚀 Which IPO should I apply for?",
                    "📈 What is SIP and compounding?",
                    "🧾 Indian Equity Taxation (LTCG / STCG)",
                    "🎯 Top Stock Buys for today"
                ]
            }

        funds_text = ""
        for f in funds:
            funds_text += (
                f"• **{f['name']}** (`{f['plan']}`)\n"
                f"  - **3Y CAGR:** `{f['cagr_3y']}%` | **5Y CAGR:** `{f['cagr_5y']}%` | **Expense Ratio:** `{f['expense_ratio']}%`\n"
                f"  - **Verdict:** `{f['verdict']}`\n"
                f"  - **Suitability:** {f['suitability']}\n\n"
            )

        reply = (
            f"### 💎 **Top-Ranked {cat_title}**\n\n"
            f"{funds_text}"
            f"💡 *Remember: Past returns do not guarantee future performance. Direct plans maximize compounding.*"
        )

        return {
            "reply": reply,
            "stock_chips": [],
            "suggested_prompts": [
                "💎 Which mutual fund portfolio is best for me?",
                "🚀 Which IPO to apply today?",
                "📈 What is SIP and compounding?",
                "🎯 Top Stock Buys today"
            ]
        }

    def _handle_fno_query(self, q: str) -> Dict[str, Any]:
        """Provides real-time F&O option chain analytics and strategy recommendations."""
        sym = "BANKNIFTY" if "bank" in q else "NIFTY"
        fno = fno_service.get_index_option_chain_summary(sym)
        strat = fno["recommended_strategy"]

        legs_text = "\n".join([f"  - **{leg['action']}** `{leg['strike']} {leg['type']}` @ approx `{leg['approx_premium']}`" for leg in strat.get("legs", [])])

        reply = (
            f"### ⚡ **{fno['symbol']} Derivatives & Option Chain Intelligence**\n\n"
            f"**Spot Price:** `₹{fno['spot_price']:,.2f}` • **Sentiment:** `{fno['sentiment']}`\n"
            f"• **Put-Call Ratio (PCR OI):** `{fno['put_call_ratio_oi']}` *(> 1.0 indicates Put writing support)*\n"
            f"• **Max Pain Strike:** `{fno['max_pain_strike']}`\n"
            f"• **Major Support (Highest Put OI):** `{fno['major_support_strike']}`\n"
            f"• **Major Resistance (Highest Call OI):** `{fno['major_resistance_strike']}`\n\n"
            f"#### 🎯 **Recommended Options Strategy: {strat['name']}**\n"
            f"• **Legs Execution:**\n{legs_text}\n"
            f"• **Net Debit / Cost:** `{strat.get('net_debit', 'N/A')}`\n"
            f"• **Max Profit Potential:** `{strat.get('max_profit', 'N/A')}` | **Risk:Reward:** `{strat.get('risk_reward', '1:2')}`\n"
            f"• **Quantitative Rationale:** {strat.get('rationale', 'High probability setup aligned with current PCR.')}\n\n"
            f"⚠️ *Risk Warning: Derivatives involve leverage. Always enforce strict stop loss limits.*"
        )

        return {
            "reply": reply,
            "stock_chips": [],
            "suggested_prompts": [
                "⚡ Bank Nifty Option Chain & PCR",
                "🌪️ What is India VIX?",
                "🎯 Top Spot Stock Buys today",
                "🚀 Which IPO to apply today?"
            ]
        }

    # =========================================================================
    # Platform, Education, Stock & General Handlers
    # =========================================================================
    def _handle_platform_support_query(self, q: str) -> Optional[Dict[str, Any]]:
        # Broker OAuth
        if any(w in q for w in ["connect broker", "broker oauth", "zerodha", "kite", "upstox", "angel one", "smartapi", "how to connect"]):
            return {
                "reply": (
                    "### 🔗 **How to Connect Your Broker Account to AlphaLens**\n\n"
                    "AlphaLens supports direct OAuth 2.0 API synchronization with India's leading SEBI-registered brokers:\n\n"
                    "1. **Zerodha Kite Connect:**\n"
                    "   - Click **Connect Investments** in your terminal navbar or onboarding wizard.\n"
                    "   - Select **Zerodha Kite** and click *Authorize API*.\n"
                    "   - You will be redirected to Zerodha's secure login to grant read-only permissions for *Holdings & Positions*.\n\n"
                    "2. **Upstox Pro API & Angel One SmartAPI:**\n"
                    "   - Select Upstox or Angel One from the broker list.\n"
                    "   - Complete OTP authentication on the official broker portal.\n\n"
                    "🛡️ **Security Guarantee:** AlphaLens uses read-only OAuth tokens. We **never** store your broker passwords or trading PINs."
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "📄 How to upload CAS statement?",
                    "🏦 What is Account Aggregator?",
                    "⚡ Try Sandbox Demo Mode",
                    "🎯 Which stocks should I buy today?"
                ]
            }

        # CAS Statement Upload
        if any(w in q for w in ["cas", "cams", "kfintech", "statement", "pdf", "mutual fund statement", "upload statement"]):
            return {
                "reply": (
                    "### 📄 **How to Upload & Parse Your CAS (Consolidated Account Statement)**\n\n"
                    "You can import all your Indian Mutual Fund holdings in seconds via a CAMS / KFintech Consolidated Account Statement:\n\n"
                    "1. **Download Your CAS PDF/Text:**\n"
                    "   - Visit the official [CAMS Online](https://mycams.camsonline.com) or [KFintech](https://mfs.kfintech.com) portal.\n"
                    "   - Request a **Detailed Consolidated Account Statement (CAS)** for your PAN.\n\n"
                    "2. **Upload to AlphaLens:**\n"
                    "   - Go to **Portfolio → Connect Investments → Upload CAS Statement**.\n"
                    "   - Drag & drop your PDF or text file.\n"
                    "   - Our parser automatically extracts Folio Numbers, Scheme Names, Units, Average NAV, and calculates real-time Mark-to-Market valuation."
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "🏦 What is Account Aggregator (AA)?",
                    "🔗 Connect Zerodha / Upstox",
                    "💼 Portfolio risk analysis",
                    "🎯 Top Buys for today"
                ]
            }

        # Account Aggregator (AA)
        if any(w in q for w in ["account aggregator", "sahamati", "aa consent", "consent", "rbi aa"]):
            return {
                "reply": (
                    "### 🏦 **What is the Account Aggregator (AA) Ecosystem?**\n\n"
                    "The **Account Aggregator (AA)** is an **RBI-regulated framework** (governed by Sahamati) that enables secure, encrypted financial data sharing across Indian financial institutions:\n\n"
                    "• 🔒 **100% Consent-Driven:** You authorize data sharing via a one-time OTP sent to your registered mobile number.\n"
                    "• 🚫 **Zero Credential Sharing:** You never disclose bank or broker passwords.\n"
                    "• ⚡ **End-to-End Encrypted:** Financial data flows directly from Financial Information Providers (FIPs) to AlphaLens under strict cryptographic consent."
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "🔗 How to connect broker?",
                    "📄 How to upload CAS statement?",
                    "💼 Portfolio health check",
                    "🎯 Top Buys for today"
                ]
            }

        return None

    def _handle_financial_education_query(self, q: str) -> Optional[Dict[str, Any]]:
        # SIP & Compounding
        if any(w in q for w in ["what is sip", "systematic investment", "compounding", "compound interest", "rupee cost averaging", "sip vs lumpsum"]):
            return {
                "reply": (
                    "### 📈 **Systematic Investment Plan (SIP) & The Power of Compounding**\n\n"
                    "A **Systematic Investment Plan (SIP)** is an investment strategy where you invest a fixed amount of money at regular intervals into mutual funds or equities:\n\n"
                    "1. **Rupee Cost Averaging:** You automatically buy more units when market prices are low and fewer units when prices are high.\n"
                    "2. **The Magic of Compounding:** Reinvesting returns over time produces exponential growth: $$A = P\\left(1 + \\frac{r}{n}\\right)^{nt}$$\n"
                    "   *Example:* Investing **₹10,000/month** at 12% CAGR over 20 years yields **~₹1 Crore** (Invested: ₹24 Lakhs, Growth: ₹76 Lakhs).\n"
                    "3. **Disciplined Financial Habit:** Automates wealth building directly from your bank account."
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "💰 How to start investing as a beginner?",
                    "💎 Which Mutual Fund is best for me?",
                    "🧾 Indian Taxation: LTCG vs STCG",
                    "🎯 Top AI stock picks today"
                ]
            }

        # Taxation
        if any(w in q for w in ["tax", "taxation", "ltcg", "stcg", "capital gains", "tax harvesting", "112a", "tax on equity"]):
            return {
                "reply": (
                    "### 🧾 **Indian Equity & Mutual Fund Taxation Guide (Post-Budget 2024)**\n\n"
                    "| Holding Period | Type of Gain | Tax Rate | Exemption Limit |\n"
                    "|---|---|---|---|\n"
                    "| **< 12 Months** | **STCG** (Short-Term Capital Gains) | **20.0%** *(Flat + Cess)* | No basic exemption |\n"
                    "| **>= 12 Months** | **LTCG** (Long-Term Capital Gains) | **12.5%** *(Flat + Cess)* | **₹1.25 Lakh / year Tax-Free** |\n\n"
                    "#### 💡 **Key Tax Saving Strategies:**\n"
                    "• **Tax Loss Harvesting:** Realize losses before March 31st to offset against taxable capital gains.\n"
                    "• **Annual ₹1.25 Lakh LTCG Exemption:** Book gains up to ₹1.25 Lakh annually and immediately reinvest to step up your cost base tax-free."
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "📈 What is SIP and compounding?",
                    "💼 Analyze my portfolio risk",
                    "🎯 Top Buys for today",
                    "⚠️ Stocks to avoid"
                ]
            }

        # Valuation
        if any(w in q for w in ["pe ratio", "p/e", "price to earnings", "valuation", "pb ratio", "p/b", "peg ratio", "ev/ebitda"]):
            return {
                "reply": (
                    "### 🔍 **Understanding P/E Ratio & Valuation Multiples**\n\n"
                    "• **Price-to-Earnings (P/E) Ratio:** $\\text{P/E} = \\frac{\\text{Market Price}}{\\text{EPS}}$. Low P/E (<20) often indicates value; high P/E (>40) prices in rapid forward growth.\n"
                    "• **Price-to-Book (P/B) Ratio:** Essential for evaluating Banks and Financials.\n"
                    "• **PEG Ratio:** $\\text{P/E} / \\text{Growth Rate}$. A PEG < 1.0 represents Growth at a Reasonable Price (GARP)."
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "📊 What are ROE and ROCE?",
                    "🎯 Top Value Accumulation picks",
                    "⚡ Prediction for Reliance"
                ]
            }

        # Stop Loss
        if any(w in q for w in ["stop loss", "sl", "risk reward", "position sizing", "risk management"]):
            return {
                "reply": (
                    "### 🛡️ **Risk Management, Stop Loss & Position Sizing**\n\n"
                    "• **1% - 2% Capital Rule:** Never risk more than 1% to 2% of total capital on any single trade.\n"
                    "• **Position Sizing Formula:** $\\text{Shares} = \\frac{\\text{Capital} \\times \\text{Risk \\%}}{\\text{Entry} - \\text{Stop Loss}}$.\n"
                    "• **Risk-to-Reward:** Always target at least **1:2 or 1:3** risk-to-reward ratios."
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "💼 Portfolio risk diagnostics",
                    "🌪️ What if NIFTY drops 5%?",
                    "🎯 Top Buys with 1:2 Risk-Reward"
                ]
            }

        # VIX
        if any(w in q for w in ["what is vix", "india vix", "volatility index"]):
            return {
                "reply": (
                    "### 🌪️ **India VIX — The Market Fear Gauge**\n\n"
                    "**India VIX** measures 30-day expected annualized volatility in NIFTY 50 based on option order books:\n\n"
                    "• **VIX < 13:** Complacent, steady bull trend.\n"
                    "• **VIX 13 - 18:** Normal healthy market swings.\n"
                    "• **VIX > 22:** Heightened market fear and large swings."
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "⚡ NIFTY Option Chain & PCR",
                    "🎯 Top Buys today",
                    "⚠️ Stocks to avoid"
                ]
            }

        return None

    def _handle_stock_inquiry(self, ticker: str) -> Dict[str, Any]:
        stock = live_pipeline.get_stock(ticker)
        if not stock:
            return {
                "reply": f"⚠️ Could not find live market data for symbol **{ticker}**. Please check the ticker name.",
                "stock_chips": [],
                "suggested_prompts": ["🎯 Top Buys for today", "⚠️ Stocks to avoid", "⚡ Prediction for Reliance"]
            }

        adv = stock.get("advisory") or advisory_engine.evaluate_advisory(stock)
        outlook = stock.get("model_outlook", {})
        targets = adv.get("targets", {})
        verdict = adv.get("verdict", "HOLD / WATCH")
        v_icon = "🟢" if "BUY" in verdict else ("🔴" if "AVOID" in verdict else "🟡")

        why_buy_text = "\n".join([f"  • {r}" for r in adv.get("why_buy_reasons", [])[:2]])
        why_avoid_text = "\n".join([f"  • {w}" for w in adv.get("why_avoid_warnings", [])[:2]])

        reply = (
            f"### {v_icon} **{stock.get('name')} ({ticker})** — **{verdict}**\n\n"
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
                {"ticker": ticker, "name": stock.get("name"), "price": f"₹{stock.get('price', 0):,.1f}", "verdict": verdict, "badge_class": adv.get("badge_class", "badge-buy")}
            ],
            "suggested_prompts": [
                f"💡 Why is {ticker} moving today?",
                "🎯 Show other Top Buy picks",
                f"⚖️ Compare {ticker} with sector peer",
                "🚀 Which IPO to apply today?"
            ]
        }

    def _handle_top_buys_query(self) -> Dict[str, Any]:
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
            "Our multi-factor quantitative models have identified high-conviction equities with optimal RSI momentum (45–65) and moving average alignment:\n\n"
            f"{cards_text}"
            "💡 *Click any stock pill below to open interactive chart and full analysis.*"
        )

        return {
            "reply": reply,
            "stock_chips": stock_chips,
            "suggested_prompts": [
                "⚠️ Which stocks should I avoid?",
                "🚀 Which IPO should I apply for?",
                "💎 Top Mutual Funds to invest in",
                "⚡ NIFTY Option Chain & PCR"
            ]
        }

    def _handle_stocks_to_avoid_query(self) -> Dict[str, Any]:
        recs = live_pipeline.get_all_recommendations()
        avoids = recs.get("stocks_to_avoid", [])[:4]

        cards_text = ""
        stock_chips = []

        for a in avoids:
            cards_text += (
                f"**🔴 {a['ticker']} — {a['name']}**\n"
                f"• Price: `₹{a['current_price']:,.1f}` | Verdict: **{a['verdict']}** (`{a['conviction_score']}% Caution`)\n"
                f"• Risk Warning: ⚠️ {a['why_avoid_warnings'][0] if a['why_avoid_warnings'] else 'Technical breakdown below key support.'}\n"
                f"• Alternative: {a.get('alternative_suggestion') or 'Defensive bluechips with healthy RSI.'}\n\n"
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
            f"{cards_text}"
            "🛡️ *Risk Rule: Capital preservation takes precedence over chasing overextended rallies.*"
        )

        return {
            "reply": reply,
            "stock_chips": stock_chips,
            "suggested_prompts": [
                "🎯 Show me safe Buy recommendations",
                "🚀 Which IPO should I apply for?",
                "💎 Which Mutual Fund is better for low risk?",
                "💼 Check my portfolio risk"
            ]
        }

    def _handle_comparison_query(self, t1: str, t2: str) -> Dict[str, Any]:
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
            f"💡 **AI Takeaway:** {t1 if adv1.get('conviction_score', 0) >= adv2.get('conviction_score', 0) else t2} shows higher relative quantitative strength."
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
                "🚀 Which IPO to apply today?"
            ]
        }

    def _handle_portfolio_overview(self) -> Dict[str, Any]:
        port = risk_engine.analyze_portfolio(live_pipeline.latest_stocks_cache)
        metrics = port.get("risk_metrics", {})

        reply = (
            "### 💼 **Portfolio Health & Factor Risk Diagnostics**\n\n"
            f"• **Current Valuation:** `₹{port.get('total_value', 0):,.2f}` (Invested: `₹{port.get('invested_capital', 0):,.2f}`)\n"
            f"• **Total P&L:** `+₹{port.get('total_pnl', 0):,.2f}` (`{port.get('total_pnl_pct', 0):+0.2f}%`)\n"
            f"• **Today's Movement:** `+₹{port.get('today_pnl', 0):,.2f}` (`{port.get('today_pnl_pct', 0):+0.2f}%`)\n\n"
            "#### 🛡️ **Risk & Attribution Metrics**\n"
            f"• **Portfolio Beta (vs NIFTY 50):** `{metrics.get('beta_vs_nifty', 1.04)}`\n"
            f"• **Sharpe Ratio:** `{metrics.get('sharpe_ratio', 1.72)}`\n"
            f"• **Value-at-Risk (1D 95% VaR):** `{metrics.get('var_95_1d_inr', '-₹4,820')}`\n"
            f"• **Conditional VaR (CVaR):** `{metrics.get('cvar_95_1d_inr', '-₹6,025')}`"
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
                "💎 Which Mutual Fund is better to diversify?"
            ]
        }

    def _handle_portfolio_stress_test(self) -> Dict[str, Any]:
        port = risk_engine.analyze_portfolio(live_pipeline.latest_stocks_cache)
        port_val = float(port.get("total_value", 321840.0))
        sim = risk_engine.simulate_scenario("nifty_drop_5pct", port_val)

        impact_pct = sim.get("expected_impact_pct", -5.2)
        impact_inr = sim.get("expected_impact_inr", -round(port_val * 0.052, 2))
        post_val = port_val + impact_inr

        reply = (
            f"### 🌪️ **Macro Stress Test: {sim.get('title', 'NIFTY 50 Falls -5.0%')}**\n\n"
            f"• **Estimated Drawdown:** `{impact_pct:+.2f}%` (`₹{impact_inr:,.0f}`)\n"
            f"• **Projected Portfolio Value:** `₹{post_val:,.2f}` (from current `₹{port_val:,.2f}`)\n"
            f"• **Recommended Action:** {sim.get('recommended_action', 'Keep core weights balanced; hedges adequate.')}"
        )

        return {
            "reply": reply,
            "stock_chips": [],
            "suggested_prompts": [
                "🎯 Show safest defensive stocks to buy",
                "💼 Back to Portfolio Overview",
                "💎 Top Mutual Funds for capital protection"
            ]
        }

    def _handle_general_reasoning_query(self, original_query: str, q: str) -> Dict[str, Any]:
        overview = live_pipeline.get_market_overview()
        n50 = overview.get("nifty_50", {})
        vix = overview.get("india_vix", {})
        regime = overview.get("market_regime", "MILD BULL")

        reply = (
            f"### 💡 **AlphaBot Financial Copilot Insight**\n\n"
            f"You asked: *\"{original_query}\"*\n\n"
            f"• **Current Market Context:** **NIFTY 50** is at `{n50.get('value', '24,850')}` with **India VIX** at `{vix.get('value', '11.4')}` in a **{regime}** regime.\n"
            f"• **Actionable Guidance:** For optimal portfolio growth, we recommend a balanced mix of high-conviction momentum equities, low-cost Direct Mutual Funds (SIP), and defined stop-loss risk parameters.\n\n"
            f"#### 🔍 **What would you like to explore?**\n"
            f"• 🚀 Ask *'Which IPO should I apply for?'*\n"
            f"• 💎 Ask *'Which Mutual Fund is best for me?'*\n"
            f"• ⚡ Ask *'NIFTY Option Chain and PCR'* for F&O derivatives\n"
            f"• 🎯 Ask about any stock forecast (*e.g. 'Prediction for Reliance'*)"
        )

        return {
            "reply": reply,
            "stock_chips": [],
            "suggested_prompts": [
                "🚀 Which IPO should I apply for?",
                "💎 Which Mutual Fund is best for me?",
                "⚡ NIFTY Option Chain & PCR",
                "🎯 Which stocks should I buy today?"
            ]
        }

    def _extract_ticker_from_query(self, q: str) -> Optional[str]:
        catalog = live_pipeline.latest_stocks_cache
        
        TICKER_STOPWORDS = {
            "WHAT", "HOW", "WHY", "WHEN", "WHERE", "WHO", "CAN", "YOU", "THE", "THIS", "THAT",
            "INDIA", "INDIAN", "BANK", "BANKS", "FINANCE", "POWER", "OIL", "GAS", "STEEL", "TECH",
            "LIFE", "MOTOR", "MOTORS", "CONSUMER", "INDUSTRIES", "HOLDINGS", "SERVICES", "ENERGY",
            "GOOD", "BEST", "TOP", "BUY", "SELL", "AVOID", "HOLD", "START", "TODAY", "DAILY",
            "STOCK", "STOCKS", "SHARE", "SHARES", "MARKET", "MARKETS", "TAX", "TAXES", "TAXATION",
            "FUND", "FUNDS", "MUTUAL", "INDEX", "OPTION", "OPTIONS", "FUTURES", "CALL", "PUT",
            "RISK", "REWARD", "PRICE", "VALUE", "GROWTH", "DIVIDEND", "BONUS", "SPLIT", "IPO", "IPOS",
            "PORTFOLIO", "ACCOUNT", "BROKER", "STATEMENT", "PREDICT", "PREDICTION", "ADVISORY", "HELP",
            "VIX", "SIP", "LTCG", "STCG", "ROE", "ROCE", "PE", "PB", "PEG", "RSI", "MACD", "ATR", "EMA", "SMA", "FNO"
        }

        pattern = r"(?:about|for|on|is|should i buy|buy|avoid|predict|prediction for|target for|analyze|check)\s+([a-zA-Z0-9\.\^]{2,15})"
        match = re.search(pattern, q)
        if match:
            candidate = match.group(1).upper().strip()
            if candidate not in TICKER_STOPWORDS:
                if candidate in catalog or candidate in ["SUZLON", "IREDA", "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "TATAMOTORS", "ZOMATO", "TRENT", "HAL", "BEL", "MAZDOCK", "RVNL", "ITC", "SBIN"]:
                    return candidate
                for ticker, stock in catalog.items():
                    if candidate in ticker or (len(candidate) >= 4 and candidate in stock.get("name", "").upper()):
                        return ticker

        words = re.findall(r"\b[A-Za-z0-9]+\b", q.upper())
        for w in words:
            if w in TICKER_STOPWORDS:
                continue
            if w in catalog:
                return w
            for ticker, stock in catalog.items():
                if w == ticker:
                    return ticker
                if len(w) >= 4 and w in stock.get("name", "").upper().split() and w not in ["LIMITED", "CORP", "CORPORATION", "ENTERPRISE", "ENTERPRISES", "COMPANY"]:
                    return ticker
        return None


chatbot_service = ChatbotService()
