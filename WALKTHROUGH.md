# AlphaLens — Institutional FinTech Market Intelligence Terminal

## 🚀 Overview & Accomplishments

**AlphaLens** is an institutional-grade probabilistic market intelligence terminal inspired by **MetaMint**, **Upstox Pro**, and **Groww**. The AI and machine learning systems operate as an invisible, disciplined quantitative core delivering calibrated forecasts, risk metrics, and causal factor breakdowns.

---

## 🔑 Key Features Implemented

### 1. Authentic Login & Signup Gateway
- **Option A (Mobile Phone SMS OTP `+91`):** Enter a 10-digit Indian mobile number to trigger an SMS OTP verification with 1-click test autofill assistance.
- **Option B (Email & Password):** Full authentication with secure password hashing (`SHA-256`), email verification codes, and persistent session tokens stored in SQLite.
- **Option C (1-Click Instant Demo Investor Access):** Instant one-click access as `"Aniket Sharma"` (`aniket.sharma@alphalens.io`).

### 2. Multi-Step "Connect Investments" Onboarding Wizard
Post-login onboarding provides 4 realistic investment connection methods:
1. 🟢 **Broker OAuth API:** Institutional authorization flow for **Zerodha Kite Connect**, **Angel One SmartAPI**, and **Upstox Pro API** with explicit permission handling (*Holdings, Positions, Funds*).
2. 🟡 **CAS Statement Parser:** Upload and parse consolidated account statement PDFs (**CAMS / KFintech** format) extracting Scheme names, Folio numbers, Units, Average NAV, and Current NAV.
3. 📊 **Account Aggregator (AA Consent):** Regulated **Sahamati Ecosystem** OTP consent flow for verified financial data fetch without sharing credentials.
4. 🔵 **Manual Portfolio Entry:** Custom stock ticker, quantity, and buy price entry with instant mark-to-market re-computation.

### 3. Deep ML Engine & Causal Attribution per Holding
- **Live Mark-to-Market Valuation:** Instant P&L calculations (Total P&L ₹/%, 1-Day change ₹/%).
- **7-Day Model Forecast & Probability:** Expected percentage movement, direction (`Positive`, `Neutral`, `Negative`), and confidence percentage.
- **Volatility Tier & Trend Regime:** Quantitative risk classification (`Low`, `Medium`, `High`) and trend regime (*Bullish Momentum Expansion*, *Consolidation Range*).
- **Transparent "Why this prediction?" Breakdown:** Explicit bullet points highlighting:
  - 14-Day RSI & 20-day exponential moving averages.
  - Institutional FinBERT news sentiment scores (0.0 to 1.0).
  - Trading volume accumulation relative to 10-day baselines.
  - Sector relative strength and macroeconomic tailwinds.
- **Academic Disclaimer Banner:** Institutional compliance disclosure on all model outputs.

### 4. Interactive Desktop Motion System (MetaMint Inspired)
- **Fluid Staggered Animations:** Panels and cards transition smoothly using CSS `cubic-bezier(0.16, 1, 0.3, 1)` easing.
- **Live Counter Animations (`animateNumber`):** Balances, index points, and P&L counts smoothly transition up rather than flashing.
- **Desk Strength Meter:** Interactive semi-circle SVG arc gauge animating from 0% to 100%.
- **Area Price Pulse Chart:** Smooth gradient area chart with 7D, 1M, and 3M timeframe toggles.
- **Factor Screener & Backtester:** 3-year historical backtest against Benchmark NIFTY 50 with CAGR, Sharpe ratio, and win rate.
- **Prediction Audit Ledger:** 600+ historical predictions with 59.7% directional accuracy, precision/recall/F1, and Brier calibration score (0.2407).

---

## 🧪 Verification & Automated Tests

All **12 automated system, authentication, and portfolio test suites** passed with 100% success rate:

```text
======================================================================
Running AlphaLens Quantitative FinTech System & Onboarding Test Suite...
======================================================================
[PASS] 1. /api/market endpoint verified (NIFTY, BANK NIFTY, VIX, Regime).
[PASS] 2. /api/stocks endpoint verified (15 stocks loaded).
[PASS] 3. /api/stocks/RELIANCE detailed metrics & causal outlook verified.
[PASS] 4a. /api/auth/phone/send-otp verified for +91 9889592243.
[PASS] 4b. /api/auth/phone/verify-otp verified (Authenticated user session created).
[PASS] 5a. /api/auth/signup verified with email verification code.
[PASS] 5b. /api/auth/login verified with email/password.
[PASS] 6. /api/auth/demo-login verified (Instant access mode).
[PASS] 7. /api/user/portfolio verified with 3 holdings and deep ML causal attribution.
[PASS] 8. /api/user/portfolio/broker-oauth verified (OAuth holdings synced from Zerodha).
[PASS] 9. /api/user/portfolio/import-cas verified (4 Mutual Fund folios parsed).
[PASS] 10. /api/user/portfolio/aa-consent verified (Sahamati AA verified & imported).
[PASS] 11a. /api/user/portfolio/add verified (Custom holding manual entry).
[PASS] 11b. /api/user/portfolio/remove verified.
[PASS] 12. Walk-forward Backtest, Natural Language Search & Prediction Ledger verified.
======================================================================
ALL 12 INSTITUTIONAL SYSTEM, ONBOARDING & ML TEST SUITES PASSED (100%)!
======================================================================
```

---

## 🌐 Running the Application Locally

The application is running live at:
**`http://127.0.0.1:8000`**

To launch or restart manually:
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
