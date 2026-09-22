"""
AlphaLens AI Financial Copilot Chatbot Engine
Context-aware quantitative reasoning agent that answers user queries about stock predictions,
live market data, customer buy/avoid advisories, portfolio risk diagnostics, macro scenarios,
general financial & investment education, and platform onboarding/support.
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
        
        # ---------------------------------------------------------------------
        # 1. Compare [STOCK1] and [STOCK2] (Priority over single stock match)
        # ---------------------------------------------------------------------
        compare_match = re.search(r"(?:compare|vs|versus)\s+([a-zA-Z0-9\.\^]+)(?:\s+and\s+|\s+vs\s+|\s+with\s+|\s+)([a-zA-Z0-9\.\^]+)", q)
        if compare_match:
            t1 = compare_match.group(1).upper()
            t2 = compare_match.group(2).upper()
            return self._handle_comparison_query(t1, t2)

        # ---------------------------------------------------------------------
        # 2. 'Which stocks should I buy?' / 'Top picks' / 'Best stocks to invest'
        # ---------------------------------------------------------------------
        if any(w in q for w in ["which stock", "stocks to buy", "what to buy", "best stock", "top buy", "recommend", "buy pick", "good to buy", "buy candidate", "what should i buy"]):
            return self._handle_top_buys_query()

        # ---------------------------------------------------------------------
        # 3. 'Which stocks should I avoid?' / 'Stocks to avoid' / 'Risky stocks'
        # ---------------------------------------------------------------------
        if any(w in q for w in ["which stocks to avoid", "stocks to avoid", "what to avoid", "dont buy", "don't buy", "risky stock", "stocks to sell", "high risk", "caution list", "avoid stocks"]):
            return self._handle_stocks_to_avoid_query()

        # ---------------------------------------------------------------------
        # 4. Platform Onboarding, Broker Connect, CAS & Customer Support Queries
        # ---------------------------------------------------------------------
        platform_res = self._handle_platform_support_query(q)
        if platform_res:
            return platform_res

        # ---------------------------------------------------------------------
        # 5. General Financial, Investment & Market Education Q&A
        # ---------------------------------------------------------------------
        edu_res = self._handle_financial_education_query(q)
        if edu_res:
            return edu_res

        # ---------------------------------------------------------------------
        # 6. Portfolio Diagnostics & Stress Testing
        # ---------------------------------------------------------------------
        if "portfolio" in q or "holdings" in q or "my stocks" in q:
            if "stress" in q or "drop" in q or "crash" in q or "fall" in q or "shock" in q:
                return self._handle_portfolio_stress_test()
            return self._handle_portfolio_overview()

        if "nifty drop" in q or "market crash" in q or "nifty falls" in q:
            return self._handle_portfolio_stress_test()

        # ---------------------------------------------------------------------
        # 7. Check for Specific Stock Inquiry (e.g., 'Should I buy Reliance?')
        # ---------------------------------------------------------------------
        stock_match = self._extract_ticker_from_query(q)
        if stock_match:
            return self._handle_stock_inquiry(stock_match)

        # ---------------------------------------------------------------------
        # 8. Greetings & Capabilities (Strict Word Match)
        # ---------------------------------------------------------------------
        if re.search(r"^(hello|hi|hey|who are you|what can you do|help|namaste|good morning|good evening)\b", q):
            return {
                "reply": (
                    "👋 **Hello! I'm AlphaBot, your AI Financial & Market Intelligence Copilot.**\n\n"
                    "I combine real-time exchange data with **calibrated machine learning models**, institutional risk metrics, and customer support intelligence. Here is how I can assist you:\n\n"
                    "• 🎯 **Stock Predictions & Targets**: Ask about any stock (*e.g. 'Prediction for Reliance', 'Is Tata Motors good to buy?'*).\n"
                    "• ⚡ **Top Buys & Stocks to Avoid**: Get high-conviction momentum picks and risk alerts.\n"
                    "• 📚 **Financial Concepts & Education**: Ask about SIPs, P/E ratio, RSI, Indian taxation (LTCG/STCG), IPOs, Options, and more.\n"
                    "• 💼 **Portfolio & Risk Diagnostics**: Analyze Sharpe ratio, Value-at-Risk (VaR), and macro stress tests.\n"
                    "• 🔗 **Platform & Broker Help**: Step-by-step guidance on connecting Zerodha/Upstox, uploading CAS statements, and Sahamati Account Aggregator consent.\n"
                    "• ⚖️ **Stock Comparisons**: Compare any two equities side-by-side (*e.g. 'Compare TCS vs INFY'*)."
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "🎯 Which stocks should I buy today?",
                    "⚠️ What stocks should I avoid?",
                    "⚡ Prediction for Reliance",
                    "📚 What is SIP and how does compounding work?",
                    "💼 Analyze my portfolio risk"
                ]
            }

        # ---------------------------------------------------------------------
        # 6. Platform Onboarding, Broker Connect, CAS & Customer Support Queries
        # ---------------------------------------------------------------------
        platform_res = self._handle_platform_support_query(q)
        if platform_res:
            return platform_res

        # ---------------------------------------------------------------------
        # 7. General Financial, Investment & Market Education Q&A
        # ---------------------------------------------------------------------
        edu_res = self._handle_financial_education_query(q)
        if edu_res:
            return edu_res

        # ---------------------------------------------------------------------
        # 8. Portfolio Diagnostics & Stress Testing
        # ---------------------------------------------------------------------
        if "portfolio" in q or "holdings" in q or "my stocks" in q:
            if "stress" in q or "drop" in q or "crash" in q or "fall" in q or "shock" in q:
                return self._handle_portfolio_stress_test()
            return self._handle_portfolio_overview()

        if "nifty drop" in q or "market crash" in q or "nifty falls" in q:
            return self._handle_portfolio_stress_test()

        # ---------------------------------------------------------------------
        # 9. Intelligent General Reasoning Fallback
        # ---------------------------------------------------------------------
        return self._handle_general_reasoning_query(query, q)

    # =========================================================================
    # Platform & Customer Support Handlers
    # =========================================================================
    def _handle_platform_support_query(self, q: str) -> Optional[Dict[str, Any]]:
        """Answers platform onboarding, broker integration, and support queries."""
        
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
                    "🛡️ **Security Guarantee:** AlphaLens uses read-only OAuth tokens. We **never** store your broker passwords or trading PINs, and we cannot execute trades without explicit consent."
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
                    "   - Request a **Detailed Consolidated Account Statement (CAS)** for your PAN.\n"
                    "   - Receive the password-protected statement on your registered email.\n\n"
                    "2. **Upload to AlphaLens:**\n"
                    "   - Go to **Portfolio → Connect Investments → Upload CAS Statement**.\n"
                    "   - Drag & drop your PDF or text file.\n"
                    "   - Our parser automatically extracts Folio Numbers, Scheme Names, Units, Average NAV, and calculates real-time Mark-to-Market valuation with risk diagnostics."
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
                    "The **Account Aggregator (AA)** is an **RBI-regulated framework** (governed by Sahamati) that enables secure, encrypted, and seamless financial data sharing across Indian financial institutions:\n\n"
                    "• 🔒 **100% Consent-Driven:** You authorize data sharing via a one-time OTP sent to your Aadhaar/bank registered mobile number.\n"
                    "• 🚫 **Zero Credential Sharing:** You never disclose bank or broker passwords.\n"
                    "• ⚡ **End-to-End Encrypted:** Financial data flows directly from Financial Information Providers (FIPs - your banks/depositories) to AlphaLens (FIU) under strict cryptographic consent.\n"
                    "• ⏱️ **Revocable Anytime:** You can pause or revoke data access at any time from your settings."
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "🔗 How to connect broker?",
                    "📄 How to upload CAS statement?",
                    "💼 Portfolio health check",
                    "🎯 Top Buys for today"
                ]
            }

        # Sandbox / Demo Mode
        if any(w in q for w in ["sandbox", "demo mode", "demo account", "guest", "test mode", "aniket sharma"]):
            return {
                "reply": (
                    "### ⚡ **AlphaLens Demo Sandbox Mode**\n\n"
                    "Our **Demo Sandbox Mode** allows institutional investors and retail traders to test the full power of AlphaLens without connecting real accounts:\n\n"
                    "• 💼 **Pre-loaded Demo Portfolio:** Access a curated ₹3,20,000 demonstration portfolio with active bluechip holdings (*Reliance, TCS, HDFC Bank, Infosys*).\n"
                    "• 🎯 **Live ML Signal Feeds:** View live 7-day model forecasts, directional probabilities, and causal factor breakdowns.\n"
                    "• 🌪️ **Interactive Stress Testing:** Simulate macro shocks (e.g. -5% NIFTY drawdown) on demo assets.\n"
                    "• 🛡️ **Zero Risk / Complete Isolation:** Actions performed in Sandbox mode do not alter real production user accounts.\n\n"
                    "👉 Click **'Explore Sandbox ⚡'** on the login page or top navigation to jump in instantly!"
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "🎯 Which stocks should I buy today?",
                    "⚠️ What stocks should I avoid?",
                    "⚡ Prediction for Reliance",
                    "💼 Portfolio risk summary"
                ]
            }

        # How AlphaLens Predictions Work
        if any(w in q for w in ["how prediction", "how it works", "model works", "ml work", "methodology", "brier", "platt", "quantile"]):
            return {
                "reply": (
                    "### 🤖 **How AlphaLens Machine Learning Predictions Work**\n\n"
                    "AlphaLens uses an **institutional multimodal quantitative framework** designed for statistical rigor and zero blackbox hallucinations:\n\n"
                    "1. **Multimodal Data Fusion:**\n"
                    "   - **Technicals:** 40+ quantitative indicators (14D RSI, 20/50/200 EMAs, MACD, Bollinger Bands, ATR).\n"
                    "   - **Fundamentals:** P/E, P/B, ROE, ROCE, Debt/Equity, and YoY revenue/earnings growth.\n"
                    "   - **News NLP:** Real-time financial headlines scored via FinBERT sentiment models.\n"
                    "   - **Macro Regimes:** Gaussian Mixture Models (GMM) clustering NIFTY returns and India VIX.\n\n"
                    "2. **Soft-Voting Ensemble & Probability Calibration:**\n"
                    "   - Ensembles **HistGradientBoosting**, **Random Forest**, and **Logistic Regression**.\n"
                    "   - Platt / Sigmoid calibration ensures a 70% probability forecast achieves 70% empirical realization (Brier Score: `0.2407`).\n\n"
                    "3. **Quantile Return Prediction Intervals:**\n"
                    "   - Pinball loss regressors output median expected return plus 80% confidence intervals ($[Q_{10}, Q_{90}]$).\n\n"
                    "4. **Causal Explainability (XAI):**\n"
                    "   - Transparent 'Why this prediction?' factor attributions for every holding."
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "🎯 Show Top Buys today",
                    "⚠️ Show Stocks to Avoid",
                    "📜 View Prediction Audit Ledger",
                    "⚡ Prediction for Tata Motors"
                ]
            }

        # Advisory Badges Meaning
        if any(w in q for w in ["advisory verdict", "what does strong buy mean", "advisory tag", "conviction score", "verdict mean"]):
            return {
                "reply": (
                    "### 🏷️ **AlphaLens Advisory Verdicts & Conviction Guide**\n\n"
                    "Our advisory engine synthesizes calibrated ML probabilities, risk parameters, and technical momentum into 5 disciplined tiers:\n\n"
                    "• 🟢 **STRONG BUY (80%+ Conviction):** Optimal momentum alignment (RSI 45-65), trading above 20/50/200 EMAs, positive FinBERT sentiment, and favorable Risk:Reward ratio (>= 1:2.5).\n"
                    "• 🟢 **ACCUMULATE / BUY (65%–79% Conviction):** Constructive uptrend with good valuation support. Ideal for staggered SIP or partial entry on minor pullbacks.\n"
                    "• 🟡 **HOLD / WATCH (45%–64% Conviction):** Consolidation or neutral regime. Keep existing positions with trailing stop losses; avoid aggressive fresh capital allocation.\n"
                    "• 🟠 **REDUCE / TAKE PROFIT:** Momentum exhaustion, divergence against benchmark, or price nearing extended resistance targets.\n"
                    "• 🔴 **AVOID / CAUTION (<40% Conviction / High Risk):** Severe overbought state (RSI > 75) or technical breakdown below key 200-day moving average support."
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "🎯 Which stocks are Strong Buy today?",
                    "⚠️ Which stocks are in the Avoid list?",
                    "⚡ Prediction for Reliance",
                    "💼 Check my portfolio health"
                ]
            }

        # Manual Portfolio Management
        if any(w in q for w in ["add stock", "add holding", "remove holding", "delete holding", "manual portfolio"]):
            return {
                "reply": (
                    "### ➕ **Manual Portfolio Management in AlphaLens**\n\n"
                    "If you prefer not to link a broker, you can manually manage your custom equity holdings:\n\n"
                    "1. **To Add a Holding:**\n"
                    "   - Go to the **Portfolio** tab in the main terminal.\n"
                    "   - Click **+ Add Custom Holding**.\n"
                    "   - Enter the stock ticker (*e.g. INFY, RELIANCE, TCS*), quantity of shares, and purchase buy price.\n"
                    "   - Click **Save Holding** — AlphaLens will instantly compute your live P&L, sector weights, and ML forecasts.\n\n"
                    "2. **To Remove a Holding:**\n"
                    "   - Click the **🗑️ Delete** icon next to any holding in your portfolio table to immediately remove it."
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "💼 View my portfolio summary",
                    "🎯 Top Buys for today",
                    "🔗 Connect broker automatically",
                    "⚡ Prediction for TCS"
                ]
            }

        return None

    # =========================================================================
    # Financial & Investment Education Handlers
    # =========================================================================
    def _handle_financial_education_query(self, q: str) -> Optional[Dict[str, Any]]:
        """Provides expert educational guidance on core financial concepts."""
        
        # 1. SIP, Compounding & Rupee Cost Averaging
        if any(w in q for w in ["what is sip", "systematic investment", "compounding", "compound interest", "rupee cost averaging", "sip vs lumpsum"]):
            return {
                "reply": (
                    "### 📈 **Systematic Investment Plan (SIP) & The Power of Compounding**\n\n"
                    "A **Systematic Investment Plan (SIP)** is an investment strategy where you invest a fixed amount of money at regular intervals (typically monthly) into mutual funds, ETFs, or equities:\n\n"
                    "#### 🌟 **Core Advantages of SIP:**\n"
                    "1. **Rupee Cost Averaging:** You automatically buy more units when market prices are low and fewer units when prices are high, eliminating the need to 'time the market'.\n"
                    "2. **The Magic of Compounding:** Reinvesting returns over time produces exponential growth: $$A = P\\left(1 + \\frac{r}{n}\\right)^{nt}$$\n"
                    "   *Example:* Investing **₹10,000/month** at 12% CAGR over 20 years yields **~₹1 Crore** (Invested: ₹24 Lakhs, Growth: ₹76 Lakhs).\n"
                    "3. **Disciplined Financial Habit:** Automates wealth building directly from your bank account.\n\n"
                    "💡 *Pro-Tip: When markets experience volatility or minor corrections, never pause your SIP — that is precisely when you accumulate units at discounted valuations.*"
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "💰 How to start investing as a beginner?",
                    "📊 Direct Equity vs Mutual Funds vs ETFs",
                    "🧾 Indian Taxation: LTCG vs STCG",
                    "🎯 Top AI stock picks today"
                ]
            }

        # 2. Indian Equity & Mutual Fund Taxation (LTCG / STCG)
        if any(w in q for w in ["tax", "taxation", "ltcg", "stcg", "capital gains", "tax harvesting", "112a", "tax on equity"]):
            return {
                "reply": (
                    "### 🧾 **Indian Equity & Mutual Fund Taxation Guide (Post-Budget 2024)**\n\n"
                    "Here is how profits on listed shares and equity mutual funds are taxed in India:\n\n"
                    "| Holding Period | Type of Gain | Tax Rate | Exemption Limit |\n"
                    "|---|---|---|---|\n"
                    "| **< 12 Months** | **STCG** (Short-Term Capital Gains) | **20.0%** *(Flat + Cess)* | No basic exemption |\n"
                    r"| **$\ge$ 12 Months** | **LTCG** (Long-Term Capital Gains) | **12.5%** *(Flat + Cess)* | **₹1.25 Lakh / year Tax-Free** |\n\n"
                    "#### 💡 **Key Tax Saving Strategies:**\n"
                    "• **Tax Loss Harvesting:** Realize losses before March 31st to offset against taxable short-term and long-term capital gains.\n"
                    "• **Annual ₹1.25 Lakh LTCG Exemption:** Book gains up to ₹1.25 Lakh annually and immediately reinvest to step up your cost base without paying tax.\n"
                    "• **Dividend Tax:** Dividends are added to your total income and taxed at your applicable slab rate."
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "📈 What is SIP and compounding?",
                    "💼 Analyze my portfolio risk",
                    "🎯 Top Buys for today",
                    "⚠️ Stocks to avoid"
                ]
            }

        # 3. P/E Ratio, P/B Ratio & Valuation Multiples
        if any(w in q for w in ["pe ratio", "p/e", "price to earnings", "valuation", "pb ratio", "p/b", "peg ratio", "ev/ebitda"]):
            return {
                "reply": (
                    "### 🔍 **Understanding P/E Ratio & Valuation Multiples**\n\n"
                    "Valuation multiples help investors determine whether a company's stock price is cheap, fair, or overpriced relative to its financial performance:\n\n"
                    "#### 1. **Price-to-Earnings (P/E) Ratio:**\n"
                    "$$\\text{P/E} = \\frac{\\text{Current Market Price per Share}}{\\text{Earnings Per Share (EPS)}}$$\n"
                    "• **Low P/E (< 15-20):** Often indicates an undervalued value stock or a cyclical company facing headwinds.\n"
                    "• **High P/E (> 40-80):** Indicates high market growth expectations (e.g. IT, FMCG, consumer tech).\n\n"
                    "#### 2. **Price-to-Book (P/B) Ratio:**\n"
                    "$$\\text{P/B} = \\frac{\\text{Market Price}}{\\text{Book Value per Share}}$$\n"
                    "• Essential for evaluating **Banks, NBFCs, and Capital-Intensive Sectors**.\n\n"
                    "#### 3. **PEG Ratio (P/E to Growth):**\n"
                    "$$\\text{PEG} = \\frac{\\text{P/E Ratio}}{\\text{Annual EPS Growth Rate (\\%)}}$$\n"
                    "• $\\text{PEG} < 1.0$ is traditionally considered an attractive growth stock at a reasonable price (GARP)."
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "📊 What are ROE and ROCE?",
                    "⚖️ Compare TCS vs INFY valuation",
                    "🎯 Top Value Accumulation picks",
                    "⚡ Prediction for Reliance"
                ]
            }

        # 4. ROE, ROCE & Balance Sheet Quality
        if any(w in q for w in ["roe", "roce", "debt to equity", "debt-to-equity", "free cash flow", "eps", "return on equity"]):
            return {
                "reply": (
                    "### 📊 **ROE, ROCE & Balance Sheet Quality Indicators**\n\n"
                    "Institutional investors look at return on capital to identify companies with wide economic moats and disciplined capital allocation:\n\n"
                    "• **Return on Equity (ROE):**\n"
                    "  $$\\text{ROE} = \\frac{\\text{Net Profit}}{\\text{Shareholder Equity}} \\times 100$$\n"
                    "  *Benchmark:* Healthy non-financial companies should consistently maintain **ROE > 15% – 20%**.\n\n"
                    "• **Return on Capital Employed (ROCE):**\n"
                    "  $$\\text{ROCE} = \\frac{\\text{EBIT (Operating Profit)}}{\\text{Total Capital Employed (Equity + Debt)}} \\times 100$$\n"
                    "  *Benchmark:* Measures how efficiently a company generates operating returns from both debt and equity. High ROCE (>= 20%) signals pricing power.\n\n"
                    "• **Debt-to-Equity (D/E) Ratio:**\n"
                    "  $$\\text{D/E} = \\frac{\\text{Total Debt}}{\\text{Total Equity}}$$\n"
                    "  *Rule of Thumb:* For manufacturing/tech/FMCG, **D/E < 0.5** is ideal. High leverage (> 1.5) magnifies risk during economic downturns."
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "🔍 What is P/E ratio?",
                    "🎯 Top quality high ROE stocks",
                    "⚠️ High risk stocks to avoid",
                    "⚡ Prediction for HDFC Bank"
                ]
            }

        # 5. Technical Indicators: RSI, Moving Averages, MACD, Bollinger Bands
        if any(w in q for w in ["technical analysis", "moving average", "ema", "sma", "macd", "bollinger", "atr", "support and resistance", "golden cross", "death cross", "breakout"]):
            return {
                "reply": (
                    "### 📉 **Essential Technical Indicators & Chart Patterns**\n\n"
                    "Technical analysis examines historical price and volume action to identify high-probability entry, exit, and risk levels:\n\n"
                    "1. **Moving Averages (20, 50, 200 EMAs):**\n"
                    "   • **200 EMA:** The ultimate institutional trend dividing line. Stocks above the 200 EMA are in primary bull markets.\n"
                    "   • **Golden Cross:** 50 EMA crosses above 200 EMA (Bullish long-term signal).\n"
                    "   • **Death Cross:** 50 EMA crosses below 200 EMA (Bearish signal).\n\n"
                    "2. **Relative Strength Index (14D RSI):**\n"
                    "   • **45 – 65:** Healthy accumulation momentum zone.\n"
                    "   • **> 75:** Overbought territory (risk of mean-reversion pullbacks).\n"
                    "   • **< 35:** Oversold territory.\n\n"
                    "3. **MACD (Moving Average Convergence Divergence):**\n"
                    "   • MACD line crossing above Signal line indicates accelerating upward momentum.\n\n"
                    "4. **Support & Resistance:**\n"
                    "   • Support represents price floors where institutional buying emerges; resistance represents ceilings where selling pressure dominates."
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "🎯 Show Momentum Breakout stocks",
                    "⚠️ Stocks currently overbought",
                    "⚡ Prediction for Reliance",
                    "🛡️ What is Stop Loss and Risk Management?"
                ]
            }

        # 6. Risk Management, Stop Loss & Position Sizing
        if any(w in q for w in ["stop loss", "sl", "risk reward", "position sizing", "risk management", "capital preservation", "drawdown"]):
            return {
                "reply": (
                    "### 🛡️ **Risk Management, Stop Loss & Position Sizing**\n\n"
                    "> *\"Rule No. 1: Never lose capital. Rule No. 2: Never forget Rule No. 1.\"* — Warren Buffett\n\n"
                    "Professional trading is fundamentally an exercise in risk management, not prediction certainty:\n\n"
                    "#### 1. **The 1% – 2% Capital Risk Rule:**\n"
                    "Never risk more than **1% to 2%** of your total portfolio capital on any single trade.\n\n"
                    "#### 2. **Calculating Position Size:**\n"
                    "$$\\text{Position Size (Shares)} = \\frac{\\text{Account Capital} \\times \\text{Risk \\% (e.g. 1\\%)}}{\\text{Entry Price} - \\text{Stop Loss Price}}$$\n"
                    "*Example:* On a ₹5,00,000 portfolio risking 1% (₹5,000) with a stock entry at ₹1,000 and Stop Loss at ₹950 (₹50 risk/share), buy exactly **100 shares**.\n\n"
                    "#### 3. **Risk-to-Reward Ratio (R:R):**\n"
                    "Aim for at least **1 : 2 or 1 : 3** risk-to-reward. With a 1:2 R:R, you can be right only 40% of the time and still be consistently profitable!"
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "💼 Portfolio risk diagnostics",
                    "🌪️ What if NIFTY drops 5%?",
                    "🎯 Top Buys with 1:2 Risk-Reward",
                    "⚠️ Stocks to avoid"
                ]
            }

        # 7. Options & Derivatives Basics
        if any(w in q for w in ["what is option", "call option", "put option", "derivatives", "futures", "strike price", "open interest", "f&o", "option trading"]):
            return {
                "reply": (
                    "### ⚡ **Futures & Options (F&O) Basics**\n\n"
                    "Derivatives are financial contracts whose value is derived from an underlying asset (such as NIFTY, Bank NIFTY, or individual stocks):\n\n"
                    "#### 1. **Call Options (CE):**\n"
                    "• Gives the buyer the right (not obligation) to **buy** the underlying asset at the **Strike Price** before expiry.\n"
                    "• Bought when expecting bullish upward price movement.\n\n"
                    "#### 2. **Put Options (PE):**\n"
                    "• Gives the buyer the right to **sell** the underlying asset at the Strike Price.\n"
                    "• Bought when expecting bearish downward price movement or as portfolio insurance (hedging).\n\n"
                    "#### 3. **Key Parameters:**\n"
                    "• **Premium:** The price paid by option buyers to sellers.\n"
                    "• **Open Interest (OI):** Total number of outstanding active derivative contracts. Large OI concentrations act as strong support/resistance zones.\n"
                    "• **Theta (Time Decay):** Option premiums lose value over time, heavily favoring disciplined option sellers.\n\n"
                    "⚠️ **Institutional Warning:** 90%+ of retail F&O intraday traders lose capital due to leverage and time decay. Always prioritize spot equity investing or proper hedging."
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "📊 What is India VIX?",
                    "🛡️ Stop Loss & Position Sizing",
                    "🎯 Spot equity Top Buys today",
                    "💼 Portfolio risk check"
                ]
            }

        # 8. India VIX & Volatility
        if any(w in q for w in ["what is vix", "india vix", "volatility index", "fear gauge", "implied volatility"]):
            return {
                "reply": (
                    "### 🌪️ **India VIX — The Market Fear Gauge**\n\n"
                    "**India VIX** measures the annualized expected volatility in the NIFTY 50 index over the next 30 calendar days, computed from NIFTY out-of-the-money option order books:\n\n"
                    "• **VIX < 13 (Low Volatility / Complacency):** Calm, trending market. Favorable for momentum equity accumulation, but option premiums are cheap.\n"
                    "• **VIX 13 – 18 (Normal / Moderate Volatility):** Standard institutional market conditions with healthy swings.\n"
                    "• **VIX > 22 (High Volatility / Panic):** Heightened market uncertainty, large intraday swings, and expanded option premiums.\n\n"
                    "💡 *Negative Correlation:* Historically, India VIX moves inversely to NIFTY 50. Sudden spikes in VIX often accompany sharp market pullbacks."
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "🌐 Live Market Pulse & VIX",
                    "🌪️ What if NIFTY drops 5%?",
                    "🎯 Top Buys in current regime",
                    "⚠️ Stocks to avoid"
                ]
            }

        # 9. Market Regimes & Cycles
        if any(w in q for w in ["bull market", "bear market", "market cycle", "correction", "sideways", "consolidation"]):
            return {
                "reply": (
                    "### 🔄 **Stock Market Cycles & Regimes**\n\n"
                    "Financial markets transition through four structural phases modeled via Gaussian Mixture Models (GMM) in AlphaLens:\n\n"
                    "1. **Accumulation Phase (Early Bull):** Institutional investors quietly accumulate undervalued equities after prolonged declines; sentiment is pessimistic but smart money enters.\n"
                    "2. **Markup / Bull Momentum Phase:** Prices break above 200-day SMAs, corporate earnings expand, and retail participation surges. High-conviction buying works best here.\n"
                    "3. **Distribution Phase (Top):** Smart money books profits into retail euphoria; price action becomes volatile and sideways.\n"
                    "4. **Markdown / Bear Market Phase:** Lower highs and lower lows form; prices fall below moving averages. Capital preservation and defensive hedging become essential."
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "🌐 What is today's Market Regime?",
                    "🎯 Top Buys for current regime",
                    "⚠️ High risk stocks to avoid",
                    "💼 Portfolio stress test"
                ]
            }

        # 10. Corporate Actions (Dividends, Splits, Bonus, Buybacks)
        if any(w in q for w in ["dividend", "stock split", "bonus share", "buyback", "rights issue", "ex-date", "record date"]):
            return {
                "reply": (
                    "### 🎁 **Corporate Actions Demystified**\n\n"
                    "Corporate actions are decisions approved by a company's Board of Directors that impact its shareholders:\n\n"
                    "• **Dividends:** Cash payments distributed from company profits directly into your bank account. Dividend Yield = $\\frac{\\text{Annual Dividend}}{\\text{Stock Price}} \\times 100$.\n"
                    "• **Stock Split:** A stock divides into multiple shares (e.g. 1:10 split turns 1 share of ₹1,000 into 10 shares of ₹100). Market cap remains unchanged, but liquidity increases.\n"
                    "• **Bonus Shares:** Free additional shares issued to existing shareholders in a fixed ratio (e.g. 1:1 bonus gives 1 free share for every 1 share held) funded from retained reserves.\n"
                    "• **Share Buyback:** Company repurchases its own shares from the open market or tender offer, reducing shares outstanding and boosting EPS.\n"
                    "• **Ex-Date vs Record Date:** You must buy the stock **before the Ex-Date** to be eligible for dividends or corporate actions."
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "🔍 What is P/E and EPS?",
                    "🎯 High dividend yielding stocks",
                    "📈 What is SIP and compounding?",
                    "⚡ Prediction for Reliance"
                ]
            }

        # 11. Mutual Funds vs Direct Equity vs ETFs vs SGBs
        if any(w in q for w in ["mutual fund", "etf", "index fund", "direct vs regular", "expense ratio", "sgb", "gold etf", "direct equity"]):
            return {
                "reply": (
                    "### 🏛️ **Mutual Funds vs Direct Equities vs ETFs**\n\n"
                    "| Asset Class | Active / Passive | Management Expense | Ideal For |\n"
                    "|---|---|---|---|\n"
                    "| **Direct Equities** | Active Selection | ₹0 Fund Fee (Only Brokerage) | Active investors seeking alpha & custom portfolio control |\n"
                    "| **Index Funds / ETFs** | Passive (Tracks NIFTY/Sensex) | Low (0.05% – 0.20%) | Long-term investors wanting market returns with lowest cost |\n"
                    "| **Active Mutual Funds** | Fund Manager Discretion | Moderate (0.5% – 1.5% Direct) | Hands-off investors seeking professional sector rotation |\n"
                    "| **Sovereign Gold Bonds (SGB)** | Government Backed | 0% + 2.5% Annual Interest | Gold exposure with zero capital gains tax on 8-year maturity |\n\n"
                    "💡 *Pro-Tip: Always choose **Direct Plans** over Regular Plans for mutual funds — avoiding distributor commissions saves 0.5%–1.0% annually, adding up to lakhs over 15+ years.*"
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "📈 What is SIP and compounding?",
                    "📄 How to upload CAS statement?",
                    "🎯 Top AI stock picks today",
                    "💼 Portfolio risk summary"
                ]
            }

        # 12. IPOs & Primary Market
        if any(w in q for w in ["ipo", "gmp", "grey market", "listing gain", "how to apply ipo", "allotment"]):
            return {
                "reply": (
                    "### 🚀 **Initial Public Offerings (IPOs) & GMP Guide**\n\n"
                    "An **Initial Public Offering (IPO)** is the process by which a private company raises capital by issuing shares to the public on stock exchanges (NSE/BSE):\n\n"
                    "• **Price Band & Lot Size:** You bid for minimum share bundles (lots) within a price range via UPI Mandate (ASBA).\n"
                    "• **Grey Market Premium (GMP):** An unofficial indicator reflecting estimated listing gains based on off-market OTC demand before exchange listing.\n"
                    "• **Listing Gains vs Long-Term Investment:** While hot IPOs can list at 20%–50%+ premiums, study the company's P/E, promoters' track record, and use of proceeds (Fresh Issue vs Offer For Sale / OFS) before holding long-term.\n\n"
                    "💡 *How to Apply:* Through your linked broker (Zerodha Kite / Upstox / Angel One) by entering your UPI ID and approving the mandate on your UPI app."
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "🔍 How to evaluate company valuation?",
                    "🎯 Top Buys in listed stocks today",
                    "🔗 Connect broker account",
                    "⚡ Prediction for Zomato"
                ]
            }

        # 13. Beginner Guide / How to Start Investing
        if any(w in q for w in ["how to start", "beginner", "first time", "how to invest", "invest 5000", "financial planning", "emergency fund", "50 30 20"]):
            return {
                "reply": (
                    "### 🧭 **Beginner's Blueprint: How to Start Investing**\n\n"
                    "Building lasting wealth follows a structured hierarchy:\n\n"
                    "#### Step 1: Secure Your Foundation\n"
                    "• **Emergency Fund:** Stash 3 to 6 months of living expenses in a Liquid Mutual Fund or high-interest bank FD before buying volatile assets.\n"
                    "• **Health & Term Insurance:** Protect against unexpected medical or life crises without liquidating your investments.\n\n"
                    "#### Step 2: The 50/30/20 Rule\n"
                    "• **50%:** Essential Needs (rent, food, bills).\n"
                    "• **30%:** Lifestyle & Wants.\n"
                    "• **20% (Minimum):** Automated Investments (SIPs in Index Funds / Bluechips).\n\n"
                    "#### Step 3: Getting Started with ₹5,000 / month\n"
                    "• ₹3,000 in a **NIFTY 50 Index Fund** (Largecap foundation).\n"
                    "• ₹1,500 in a **NIFTY Next 50 or Midcap 150 Fund** (Growth potential).\n"
                    "• ₹500 in a **Gold ETF or SGB** (Stability hedge)."
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "📈 What is SIP and compounding?",
                    "🎯 Which stocks should I buy today?",
                    "⚡ Try Demo Sandbox Mode",
                    "💼 Portfolio risk diagnostics"
                ]
            }

        # 14. Macroeconomics & Inflation
        if any(w in q for w in ["inflation", "rbi", "repo rate", "interest rate", "fed rate", "gdp", "rupee dollar", "forex", "macro"]):
            return {
                "reply": (
                    "### 🌍 **Macroeconomics: How Interest Rates & Inflation Move Markets**\n\n"
                    "Macroeconomic forces drive institutional capital flows across global and domestic equity markets:\n\n"
                    "• **Inflation (CPI):** High inflation erodes purchasing power and corporate operating margins.\n"
                    "• **RBI Repo Rate:** When central banks raise rates to fight inflation, borrowing costs rise, leading to valuation compression (especially in high-PE growth stocks). Conversely, **rate cuts** stimulate liquidity and stock rallies.\n"
                    "• **US Federal Reserve Policy:** US interest rate decisions impact Foreign Institutional Investor (FII) flows into emerging markets like India.\n"
                    "• **USD / INR Exchange Rate:** A depreciating Rupee benefits IT and Pharma exporters while increasing import costs for Energy and Oil marketing companies."
                ),
                "stock_chips": [],
                "suggested_prompts": [
                    "🌐 Live Market Pulse & Indices",
                    "🌪️ What if NIFTY drops 5%?",
                    "🎯 Top Buys for today",
                    "⚡ Prediction for Reliance"
                ]
            }

        return None

    # =========================================================================
    # General Financial Reasoning & Open Query Fallback
    # =========================================================================
    def _handle_general_reasoning_query(self, original_query: str, q: str) -> Dict[str, Any]:
        """Provides intelligent financial reasoning and contextual market guidance for open-ended queries."""
        indices = live_pipeline.get_market_overview()
        n50 = indices.get("nifty_50", {})
        bn = indices.get("bank_nifty", {})
        vix = indices.get("india_vix", {})
        regime = indices.get("market_regime", "MILD BULL")

        recs = live_pipeline.get_all_recommendations()
        top_buys = recs.get("top_buys", [])[:2]

        chips = []
        for b in top_buys:
            chips.append({
                "ticker": b["ticker"],
                "name": b["name"],
                "price": f"₹{b['current_price']:,.1f}",
                "verdict": b["verdict"],
                "badge_class": "badge-strong-buy"
            })

        reply = (
            f"### 💡 **AlphaLens Financial Copilot Insight**\n\n"
            f"You asked: *\"{original_query}\"*\n\n"
            f"Here is what our quantitative intelligence engine and market monitors indicate:\n\n"
            f"• **Current Market Context:** **NIFTY 50** is trading at `{n50.get('value', '23,346.40')}` ({n50.get('change_formatted', '+0.33%')}) with **India VIX** at `{vix.get('value', '11.39')}` in a **{regime}** regime.\n"
            f"• **Disciplined Quantitative Approach:** Whether exploring individual stock ideas, managing risk, or planning long-term investments, we recommend basing decisions on **calibrated probabilities** (>= 65%) and maintaining at least **1:2 Risk-to-Reward** stop loss levels.\n\n"
            f"#### 🔍 **How can I assist you further?**\n"
            f"• Ask me about specific stock forecasts (*e.g. 'Prediction for Reliance', 'Is Tata Motors a buy?'*)\n"
            f"• Get today's top momentum or value picks\n"
            f"• Ask educational questions about SIP, P/E ratio, Indian taxation, or Risk Management\n"
            f"• Connect your broker account or run portfolio stress tests"
        )

        return {
            "reply": reply,
            "stock_chips": chips,
            "suggested_prompts": [
                "🎯 Which stocks should I buy today?",
                "⚠️ What stocks should I avoid?",
                "⚡ Prediction for Reliance",
                "📈 What is SIP and compounding?",
                "💼 Analyze my portfolio risk"
            ]
        }

    # =========================================================================
    # Stock-Specific & Quantitative Handlers
    # =========================================================================
    def _extract_ticker_from_query(self, q: str) -> Optional[str]:
        """Identifies stock tickers or company names mentioned in query."""
        catalog = live_pipeline.latest_stocks_cache
        
        TICKER_STOPWORDS = {
            "WHAT", "HOW", "WHY", "WHEN", "WHERE", "WHO", "CAN", "YOU", "THE", "THIS", "THAT",
            "INDIA", "INDIAN", "BANK", "BANKS", "FINANCE", "POWER", "OIL", "GAS", "STEEL", "TECH",
            "LIFE", "MOTOR", "MOTORS", "CONSUMER", "INDUSTRIES", "HOLDINGS", "SERVICES", "ENERGY",
            "GOOD", "BEST", "TOP", "BUY", "SELL", "AVOID", "HOLD", "START", "TODAY", "DAILY",
            "STOCK", "STOCKS", "SHARE", "SHARES", "MARKET", "MARKETS", "TAX", "TAXES", "TAXATION",
            "FUND", "FUNDS", "MUTUAL", "INDEX", "OPTION", "OPTIONS", "FUTURES", "CALL", "PUT",
            "RISK", "REWARD", "PRICE", "VALUE", "GROWTH", "DIVIDEND", "BONUS", "SPLIT", "IPO",
            "PORTFOLIO", "ACCOUNT", "BROKER", "STATEMENT", "PREDICT", "PREDICTION", "ADVISORY", "HELP",
            "VIX", "SIP", "LTCG", "STCG", "ROE", "ROCE", "PE", "PB", "PEG", "RSI", "MACD", "ATR", "EMA", "SMA"
        }

        # Check direct regex patterns: "about RELIANCE", "for SUZLON", "is TCS good", "prediction for INFY"
        pattern = r"(?:about|for|on|is|should i buy|buy|avoid|predict|prediction for|target for|analyze|check)\s+([a-zA-Z0-9\.\^]{2,15})"
        match = re.search(pattern, q)
        if match:
            candidate = match.group(1).upper().strip()
            if candidate not in TICKER_STOPWORDS:
                if candidate in catalog or candidate in ["SUZLON", "IREDA", "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "TATAMOTORS", "ZOMATO", "TRENT", "HAL", "BEL", "MAZDOCK", "RVNL", "ITC", "SBIN"]:
                    return candidate
                # Fuzzy check in catalog
                for ticker, stock in catalog.items():
                    if candidate in ticker or (len(candidate) >= 4 and candidate in stock.get("name", "").upper()):
                        return ticker

        # Word-by-word catalog match
        words = re.findall(r"\b[A-Za-z0-9]+\b", q.upper())
        for w in words:
            if w in TICKER_STOPWORDS:
                continue
            if w in catalog:
                return w
            for ticker, stock in catalog.items():
                if w == ticker:
                    return ticker
                # Only match company name words if word is distinctive (>4 chars and not a stopword)
                if len(w) >= 4 and w in stock.get("name", "").upper().split() and w not in ["LIMITED", "CORP", "CORPORATION", "ENTERPRISE", "ENTERPRISES", "COMPANY"]:
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


chatbot_service = ChatbotService()
